import math
from fastapi import HTTPException
import pandas as pd
from ..models.models import Dataset
from ..schemas.dataset import DatasetVisualized,chart

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

def data_engine_visual(dataset:Dataset,payload:DatasetVisualized):
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

    if payload.x_column not in df.columns:
        raise KeyError(f"X-Axis column '{payload.x_column}' not found in dataset columns.")
        
    if payload.y_column and payload.y_column not in df.columns:
        raise KeyError(f"Y-Axis column '{payload.y_column}' not found in dataset columns.")
    
    chart_type = payload.chart_type
    x_col = payload.x_column
    y_col = payload.y_column
    if chart_type in [chart.bar, chart.line, chart.pie]:
        if y_col:
            if pd.api.types.is_numeric_dtype(df[y_col]):
                summary = df.groupby(x_col)[y_col].mean().dropna().head(15)
                labels = [str(k) for k in summary.index]
                values = [None if (math.isnan(v) or math.isinf(v)) else float(v) for v in summary.values]
                
                return {
                    "mode": "single_series",
                    "labels": labels,
                    "values": values
                }
                

            else:
                top_x = df[x_col].value_counts().head(10).index
                top_y = df[y_col].value_counts().head(5).index
                filtered_df = df[df[x_col].isin(top_x) & df[y_col].isin(top_y)]

                ct = pd.crosstab(filtered_df[x_col], filtered_df[y_col])
                
                labels = [str(idx) for idx in ct.index] 

                datasets = []
                for y_category in ct.columns:
                    series_values = [int(v) for v in ct[y_category].values]
                    datasets.append({
                        "label": str(y_category), 
                        "data": series_values    
                    })
                
                return {
                    "mode": "multi_series",
                    "labels": labels,
                    "datasets": datasets
                }
                
    else :
        summary = df[x_col].value_counts().dropna().head(15)
        return {
                "mode": "single_series_no_y",
                "labels": [str(k) for k in summary.index],
                "values": [float(v) for v in summary.values]
                }

def data_engine_columns(dataset:Dataset):
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
    columns= list(df.columns)
    return {
       'columns':columns
    }
