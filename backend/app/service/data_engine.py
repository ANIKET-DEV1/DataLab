import math
from fastapi import HTTPException
import pandas as pd
from ..models.models import Dataset

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