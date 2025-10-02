# utils/preprocessing.py
import re
import pandas as pd
import numpy as np


URL_PATTERN = re.compile(r"(https?://\S+|www\.\S+)", flags=re.IGNORECASE)
def clean_text_for_indobert(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.strip()
    text = re.sub(r'@\w+', '', text)          # hapus mention
    text = re.sub(r'#\w+', '', text)          # hapus hashtag
    text = re.sub(r'RT[\s]+', '', text)       # hapus retweet
    text = re.sub(URL_PATTERN, '', text)      # hapus link
    text = re.sub(r'\s+', ' ', text).strip()  # normalisasi spasi
    return text

def standardize_dates(df: pd.DataFrame, col="Tanggal Reviews") -> pd.DataFrame:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    else:
        df[col] = pd.NaT
    return df

def ensure_required_columns(df: pd.DataFrame, required_cols):
    for c in required_cols:
        if c not in df.columns:
            df[c] = np.nan
    return df
def normalize_column_names(df: pd.DataFrame):
    col_map = {}
    for col in df.columns:
        c = col.strip().lower()
        if c in ["tanggal", "tanggal reviews", "date", "created_at"]:
            col_map[col] = "Tanggal Reviews"
        elif c in ["review", "reviews", "ulasan", "comment", "komentar"]:
            col_map[col] = "Reviews"
        elif c in ["user", "username", "user_name", "pengguna", "nama"]:
            col_map[col] = "User"
        elif c in ["rate", "rating", "bintang"]:
            col_map[col] = "Rate"
        elif c in ["lokasi", "location", "pos_office", "pos_office_branch", "pos_office_branch".lower()]:
            col_map[col] = "lokasi"
        elif c in ["aplikasi", "app", "application"]:
            col_map[col] = "Aplikasi"
        else:
            pass
    if col_map:
        df = df.rename(columns=col_map)
    return df
