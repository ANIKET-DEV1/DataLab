import os
import math
import pandas as pd
from ..models.models import Dataset
from ..schemas import dataset as ds
from ..exceptions_handler.handle_expection import ValidationError, DataProcessingError, DataLabExceptionHandler

def sanitize_dict_list(raw_records: list[dict]) -> list[dict]:
    clean_records = []
    for row in raw_records:
        clean_row = {}
        for key, value in row.items():
            # If it's a NaN/Infinity float or missing Pandas type, switch to None
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                clean_row[key] = None
            elif pd.isna(value):
                clean_row[key] = None
            else:
                clean_row[key] = value
        clean_records.append(clean_row)
    return clean_records

def data_engine_preview(dataset: Dataset):
    file_path = dataset.file_path
    ext = dataset.file_type.value
    try:
        if ext == "csv":
            df = pd.read_csv(file_path, nrows=20)
        elif ext == "xlsx":
            df = pd.read_excel(file_path, nrows=20)
        elif ext == "json":
            df = pd.read_json(file_path)
            df = df.head(20)
        else:
            raise ValidationError("Preview not supported for this file type.")
    except DataLabExceptionHandler:
        raise
    except Exception as e:
        raise DataProcessingError(f"Failed reading dataset file asset: {str(e)}")

    raw_preview = df.head(10).to_dict(orient="records")

    summary_desc = df.describe(include='all').reset_index().to_dict(orient="records")

    null_info = []
    for col in df.columns:
        null_info.append({
            "Column": col,
            "Data Type": str(df[col].dtype),
            "Non-Null Count": int(df[col].notnull().sum()),
            "Null Count": int(df[col].isnull().sum())
        })

    return {
        "preview": sanitize_dict_list(raw_preview),
        "describe": sanitize_dict_list(summary_desc),
        "info": null_info  
    }

def _read_dataframe(dataset: Dataset, nrows:int | None = None) -> pd.DataFrame:
    file_path = dataset.file_path
    ext = dataset.file_type.value
    try:
        if ext == "csv":
            return pd.read_csv(file_path, nrows=nrows)
        elif ext == "xlsx":
            return pd.read_excel(file_path, nrows=nrows)
        elif ext == "json":
            return pd.read_json(file_path).head(nrows)
        else:
            raise ValidationError("Preview not supported for this file type.")
    except DataLabExceptionHandler:
        raise
    except Exception as e:
        raise DataProcessingError(f"Failed to read dataset: {str(e)}")

def _safe_float(v):
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return float(v)


def data_engine_columns(dataset: Dataset) -> dict:
    df = _read_dataframe(dataset) 
    null_counts = df.isnull().sum()
    return {
        "columns": list(df.columns),
        "columns-dataTypes": {
            str(col): str(dtype) for col, dtype in df.dtypes.items()
        },
        "columns-null": {
            str(col): int(count) for col, count in null_counts.items()
        }
    }


CHART_SINGLE_SERIES = {"bar", "line", "pie", "hist"}
def data_engine_visual(dataset: Dataset, payload: ds.DatasetVisualized) -> dict:
    df = _read_dataframe(dataset, nrows=500)

    x_col = payload.x_column
    y_col = payload.y_column
    chart_type = payload.chart_type.lower()

    # Validate columns exist
    if x_col not in df.columns:
        raise ValidationError(f"Column '{x_col}' not found in dataset.")
    if y_col and y_col not in df.columns:
        raise ValidationError(f"Column '{y_col}' not found in dataset.")

    # ── Scatter ──────────────────────────────────────────────────
    if chart_type == "scatter":
        if not y_col:
            raise ValidationError("Scatter chart requires a Y column.")
        if not pd.api.types.is_numeric_dtype(df[x_col]) or not pd.api.types.is_numeric_dtype(df[y_col]):
            raise ValidationError("Scatter chart requires both columns to be numeric.")

        scatter_data = [
            {"x": _safe_float(row[x_col]), "y": _safe_float(row[y_col])}
            for _, row in df[[x_col, y_col]].dropna().head(200).iterrows()
        ]
        return {"mode": "scatter", "scatterData": scatter_data}

    # ── Bar / Line / Pie / Hist ───────────────────────────────────
    if chart_type in CHART_SINGLE_SERIES:
        if not y_col:
            # Frequency count of x column
            summary = df[x_col].value_counts().dropna().head(15)
            return {
                "mode": "single_series",
                "labels": [str(k) for k in summary.index],
                "values": [int(v) for v in summary.values],
            }

        if pd.api.types.is_numeric_dtype(df[y_col]):
            # Numeric y → group by x, take mean
            summary = df.groupby(x_col)[y_col].mean().dropna().head(15)
            return {
                "mode": "single_series",
                "labels": [str(k) for k in summary.index],
                "values": [_safe_float(v) for v in summary.values],
            }

        top_x = df[x_col].value_counts().head(10).index
        top_y = df[y_col].value_counts().head(5).index
        filtered = df[df[x_col].isin(top_x) & df[y_col].isin(top_y)]
        ct = pd.crosstab(filtered[x_col], filtered[y_col])

        return {
            "mode": "multi_series",
            "labels": [str(i) for i in ct.index],
            "datasets": [
                {"label": str(col), "data": [int(v) for v in ct[col].values]}
                for col in ct.columns
            ],
        }

    raise ValidationError(f"Unknown chart type: '{chart_type}'.")

def column_wise_clean(dataset: Dataset, payload: ds.ColumnWiseClean):
    try:
        df = _read_dataframe(dataset)
        column = payload.column_name
        
        if column not in df.columns:
            raise ValidationError(f"Column '{column}' not found.")

        clean_type = payload.clean_type
        if clean_type == 'drop-na':
            df.dropna(subset=[column], inplace=True)
            
        elif clean_type == 'fill-na':
            strategy = payload.fill_type
            if strategy in ["mean", "mode"]:
                if pd.api.types.is_numeric_dtype(df[column]):
                    df[column] = df[column].fillna(df[column].mean())
                else:
                    mode = df[column].mode()
                    if not mode.empty:
                        df[column] = df[column].fillna(mode[0])
            elif strategy == 'custom':
                value = payload.custom_fill_value
                if pd.api.types.is_numeric_dtype(df[column]):
                    try:
                        numeric_value = float(value) if '.' in value else int(value)
                        df[column] = df[column].fillna(numeric_value)
                    except ValueError:
                        df[column] = df[column].fillna(value)
                else:
                    df[column] = df[column].fillna(value)


        temp_file_path = f"{dataset.file_path}.tmp"
        

        if dataset.file_type == "csv":
            df.to_csv(temp_file_path, index=False)
        elif dataset.file_type == "xlsx":
            df.to_excel(temp_file_path, index=False)
        elif dataset.file_type == "json":
            df.to_json(temp_file_path, index=False)
        import os
        os.replace(temp_file_path, dataset.file_path)
        raw_preview = df.head(10).to_dict(orient="records")
        null_counts = df.isnull().sum()

        return {
            "preview": sanitize_dict_list(raw_preview),
            "columns": list(df.columns),
            "columns-dataTypes": {str(col): str(dtype) for col, dtype in df.dtypes.items()},
            "columns-null": {str(col): int(count) for col, count in null_counts.items()}
        }

    except DataLabExceptionHandler:
        raise  
    except Exception as e:
        print(f"CRITICAL ENGINE FAULT: {str(e)}")
        raise DataProcessingError("Internal Cleaning Engine Server Error")
    
def overall_clean(dataset :Dataset, payload: ds.overallclean):
    try:
        df = _read_dataframe(dataset)
        
        clean_type = payload.clean_type
        if clean_type == 'drop-na':
            if payload.axis == 0:
                df.dropna(axis=0,inplace=True)
            elif payload.axis == 1:
                df.dropna(axis=1,inplace=True)
            else:
                raise ValidationError("Please select a valid axis (0 for rows, 1 for columns).")
        elif clean_type == 'fill-na':
            raw_val = str(payload.custom_fill_value).strip()

            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    try:
                        numeric_val = float(raw_val) if '.' in raw_val else int(raw_val)
                        df[col] = df[col].fillna(numeric_val)
                    except ValueError:
                        print(f"Skipping global fill on numeric column '{col}': '{raw_val}' cannot be safely cast.")
                        continue
                elif pd.api.types.is_datetime64_any_dtype(df[col]):
                    try:
                        datetime_val = pd.to_datetime(raw_val)
                        df[col] = df[col].fillna(datetime_val)
                    except (ValueError, TypeError):
                        continue

                else:
                    df[col] = df[col].fillna(raw_val)
            

        else:
            raise ValidationError("Please select a valid cleaning strategy ('fill-na' or 'drop-na').")
        temp_file_path = f"{dataset.file_path}.tmp"
        

        if dataset.file_type == "csv":
            df.to_csv(temp_file_path, index=False)
        elif dataset.file_type == "xlsx":
            df.to_excel(temp_file_path, index=False)
        elif dataset.file_type == "json":
            df.to_json(temp_file_path, index=False)
        import os
        os.replace(temp_file_path, dataset.file_path)
    

        return {
            'message':'Successfully cleaned dataset.'
        }

    except DataLabExceptionHandler:
        raise  
    except Exception as e:
        print(f"CRITICAL ENGINE FAULT: {str(e)}")
        raise DataProcessingError("Failed to apply overall dataset cleaning operation.")
    
def rename_column(dataset: Dataset, payload: ds.renameColumn):
    try:
        df = _read_dataframe(dataset)
        
        old_column = payload.old_column
        if old_column not in df.columns:
            raise ValidationError(f"Column '{old_column}' not found in dataset.")
        

        newColName = str(payload.new_name_columns)
        if newColName and newColName.strip()!='':
            df.rename(columns={old_column:newColName}, inplace=True)
        else:
            raise ValidationError("Please provide a non-empty new column name.")
        temp_file_path = f"{dataset.file_path}.tmp"
        
        if dataset.file_type == "csv":
            df.to_csv(temp_file_path, index=False)
        elif dataset.file_type == "xlsx":
            df.to_excel(temp_file_path, index=False)
        elif dataset.file_type == "json":
            df.to_json(temp_file_path, index=False)
        import os
        os.replace(temp_file_path, dataset.file_path)
    

        return {
            'message':'Successfully renamed column.'
        }

    except DataLabExceptionHandler:
        raise  
    except Exception as e:
        print(f"CRITICAL ENGINE FAULT: {str(e)}")
        raise DataProcessingError("Failed to rename column.")

