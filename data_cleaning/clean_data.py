import argparse
from pathlib import Path
import pandas as pd
import re

# Required non-empty fields (clean & drop if empty)
REQUIRED_COLS = ["user_id", "name", "time", "rating", "text", "gmap_id"]

# Full, fixed output schema & order (guarantees headers, keeps pics/resp)
OUTPUT_COLS = ["user_id", "name", "time", "rating", "text", "pics", "resp", "gmap_id"]

# Tokens treated as empty (case-insensitive)
EMPTY_TOKENS = {"", "nan", "none", "null", "n/a", "na"}

# Whitespace normalizers
RE_ZERO_WIDTH = re.compile(r"[\u200B-\u200D\uFEFF]")
RE_WS_MULTI   = re.compile(r"\s+")

def _clean_string_series(s: pd.Series) -> pd.Series:
    s = s.astype("string")
    s = s.str.replace(RE_ZERO_WIDTH, "", regex=True)
    s = s.str.replace(RE_WS_MULTI, " ", regex=True)
    s = s.str.strip()
    lower = s.str.lower()
    s = s.mask(lower.isin(EMPTY_TOKENS))
    return s

def _clean_chunk(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    # Ensure all OUTPUT_COLS exist so schema is stable (fill missing)
    for col in OUTPUT_COLS:
        if col not in df.columns:
            df[col] = pd.NA

    # Clean only the required columns (do NOT touch pics/resp)
    for col in REQUIRED_COLS:
        df[col] = _clean_string_series(df[col])

    # Drop rows missing any required field (after cleaning)
    df = df.dropna(subset=REQUIRED_COLS)

    # Reindex to fixed output order (ensures header consistency)
    df = df[OUTPUT_COLS]
    return df

def _write_chunk(out_path: Path, df: pd.DataFrame, wrote_header_flag: dict):
    if df.empty:
        return
    df.to_csv(
        out_path,
        index=False,
        mode="a" if wrote_header_flag["done"] else "w",
        header=not wrote_header_flag["done"],
        encoding="utf-8",
    )
    wrote_header_flag["done"] = True

def json_to_clean_csv(input_file: str, output_file: str, chunksize: int = 100_000):
    in_path = Path(input_file)
    out_path = Path(output_file)

    # Reset output file if exists
    if out_path.exists():
        out_path.unlink()

    total_in = total_out = 0
    wrote_header = {"done": False}

    # Try JSON Lines (streaming)
    try:
        for chunk in pd.read_json(in_path, lines=True, chunksize=chunksize):
            total_in += len(chunk)
            cleaned = _clean_chunk(chunk)
            total_out += len(cleaned)
            _write_chunk(out_path, cleaned, wrote_header)
        if total_in > 0:
            print(f"[JSONL mode] Rows in: {total_in}, rows out: {total_out}, removed: {total_in - total_out}")
            print(f"Clean CSV saved to: {out_path}")
            return
    except Exception as e_jsonl:
        jsonl_err = e_jsonl

    # Fallback: array JSON (loads whole file)
    try:
        df = pd.read_json(in_path)
        total_in = len(df)
        cleaned = _clean_chunk(df)
        total_out = len(cleaned)
        _write_chunk(out_path, cleaned, wrote_header)
        print(f"[Array JSON mode] Rows in: {total_in}, rows out: {total_out}, removed: {total_in - total_out}")
        print(f"Clean CSV saved to: {out_path}")
    except Exception as e_array:
        print("Error: could not parse as JSON Lines or array JSON.")
        print(f"- JSON Lines error: {jsonl_err}")
        print(f"- Array JSON error: {e_array}")
        print("Tips:")
        print(" • If your file has one JSON object per line, use JSONL (preferred for large files).")
        print(" • If it starts with '[' and ends with ']', it’s array JSON (requires enough RAM).")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Convert reviews JSON/JSONL to a cleaned CSV with stable headers.")
    ap.add_argument("input_file", help="Path to input JSON/JSONL file")
    ap.add_argument("output_file", help="Path to output CSV")
    ap.add_argument("--chunksize", type=int, default=100000, help="Chunk size for JSONL streaming")
    args = ap.parse_args()
    json_to_clean_csv(args.input_file, args.output_file, args.chunksize)