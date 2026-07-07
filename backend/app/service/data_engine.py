import os
import math
from fastapi import HTTPException
import pandas as pd
from ..models.models import Dataset
from ..schemas.dataset import DatasetVisualized,chart,ColumnWiseClean,FillStrategy,CleanStrategy

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
            raise HTTPException(status_code=400, detail="Preview not supported for this file type.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed reading dataset file asset: {str(e)}")

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
            raise HTTPException(status_code=400, detail="Preview not supported for this file type.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read dataset: {str(e)}")

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
def data_engine_visual(dataset: Dataset, payload: DatasetVisualized) -> dict:
    df = _read_dataframe(dataset, nrows=500)

    x_col = payload.x_column
    y_col = payload.y_column
    chart_type = payload.chart_type.lower()

    # Validate columns exist
    if x_col not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{x_col}' not found in dataset.")
    if y_col and y_col not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{y_col}' not found in dataset.")

    # ── Scatter ──────────────────────────────────────────────────
    if chart_type == "scatter":
        if not y_col:
            raise HTTPException(status_code=400, detail="Scatter chart requires a Y column.")
        if not pd.api.types.is_numeric_dtype(df[x_col]) or not pd.api.types.is_numeric_dtype(df[y_col]):
            raise HTTPException(status_code=400, detail="Scatter chart requires both columns to be numeric.")

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

    raise HTTPException(status_code=400, detail=f"Unknown chart type: '{chart_type}'.")

def column_wise_clean(dataset: Dataset, payload: ColumnWiseClean):
    try:
        df = _read_dataframe(dataset)
        column = payload.column_name
        
        if column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{column}' not found.")

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

    except HTTPException:
        raise  
    except Exception as e:
        print(f"CRITICAL ENGINE FAULT: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Cleaning Engine Server Error")