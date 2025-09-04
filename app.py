import streamlit as st
import pandas as pd
import glob
import os
import re

# ---- Page Setup ----
st.set_page_config(page_title="Nike Order Color Summary", page_icon="📦", layout="wide")
st.title("📦 Nike Order Color Summary Extractor")

# ---- UI Controls ----
col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    folder = st.text_input("Folder with .txt files", "data/")
with col2:
    sizes_input = st.text_input("SIZE(s) (comma separated, e.g., 47x39,47x33)", "47x39,47x33")
with col3:
    merge_totals = st.checkbox("Merge totals across files (ignore FILENAME)", value=True)

filter_orderno = st.text_input("Filter ORDERNO (optional, exact or partial match)", "")
filter_nikepo  = st.text_input("Filter NIKEPO (optional, exact or partial match)", "")

sizes = {s.strip().lower() for s in sizes_input.split(",") if s.strip()}
output_csv = "filtered_summary.csv"
output_xlsx = "filtered_summary.xlsx"

# ---- Helpers ----
NEEDED_COLS = ["ORDERNO", "NIKEPO", "XCOLORBAR"]

def size_from_filename(path):
    """Extract SIZE like 47x39 from filename"""
    m = re.search(r"(\d{2,}x\d{2,})", os.path.basename(path), flags=re.IGNORECASE)
    return m.group(1).lower() if m else ""

def passes_text_filter(value, pattern):
    if not pattern:
        return True
    return pattern.lower().strip() in str(value).lower().strip()

# ---- Run ----
if st.button("Run Filter & Export"):
    files = glob.glob(os.path.join(folder, "*.txt"))
    if not files:
        st.error("No .txt files found in the given folder.")
        st.stop()

    all_parts = []
    progress = st.progress(0)
    for i, file in enumerate(files, start=1):
        try:
            df = pd.read_csv(file, sep="\t", dtype=str, quoting=0, engine="python")
        except Exception:
            df = pd.read_csv(file, sep="\t", dtype=str)

        df.columns = df.columns.str.strip().str.upper()

        # only keep files with needed cols
        if not all(c in df.columns for c in NEEDED_COLS):
            progress.progress(i / len(files))
            continue

        file_size = size_from_filename(file)
        if file_size not in sizes:
            progress.progress(i / len(files))
            continue

        # Apply filters
        filtered = df.copy()
        if filter_orderno:
            filtered = filtered[filtered["ORDERNO"].apply(lambda v: passes_text_filter(v, filter_orderno))]
        if filter_nikepo:
            filtered = filtered[filtered["NIKEPO"].apply(lambda v: passes_text_filter(v, filter_nikepo))]

        if not filtered.empty:
            grp_cols = ["ORDERNO", "NIKEPO", "XCOLORBAR"]
            part = (
                filtered.groupby(grp_cols, dropna=False)
                .size()
                .reset_index(name="QTY")
            )
            part["SIZE"] = file_size
            part["FILENAME"] = os.path.basename(file)
            all_parts.append(part)

        progress.progress(i / len(files))

    if not all_parts:
        st.warning("No matching data found for the given filters.")
        st.stop()

    final_df = pd.concat(all_parts, ignore_index=True)

    # Merge totals across files if requested
    if merge_totals:
        final_df = (
            final_df
            .groupby(["ORDERNO", "NIKEPO", "XCOLORBAR", "SIZE"], as_index=False)["QTY"]
            .sum()
        )

    # Sort nicely
    final_df = final_df.sort_values(["ORDERNO", "NIKEPO", "SIZE", "XCOLORBAR"]).reset_index(drop=True)

    # ---- Custom Output Formatting ----
    final_df["COLOR+SIZE"] = final_df["XCOLORBAR"] + " " + final_df["SIZE"]

    # Compute ORDERNO summary with total QTY
    orderno_totals = final_df.groupby("ORDERNO", as_index=False)["QTY"].sum()
    orderno_totals["ORDERNO_SUMMARY"] = orderno_totals["ORDERNO"] + "-" + orderno_totals["QTY"].astype(str)

    # Merge summary back
    final_df = final_df.merge(orderno_totals[["ORDERNO", "ORDERNO_SUMMARY"]], on="ORDERNO", how="left")

    # Final export structure
    export_df = final_df[["NIKEPO", "COLOR+SIZE", "ORDERNO_SUMMARY", "QTY"]]
    export_df.columns = ["NIKEPO", "COLOR+SIZE", "ORDERNO", "QTY"]

    # ---- Export ----
    export_df.to_csv(output_csv, index=False)
    with pd.ExcelWriter(output_xlsx, engine="xlsxwriter") as writer:
        export_df.to_excel(writer, sheet_name="Summary", index=False)

    st.success("✅ Exported results")
    st.dataframe(export_df, use_container_width=True)

    st.download_button("📥 Download CSV", data=export_df.to_csv(index=False).encode("utf-8"),
                       file_name=output_csv, mime="text/csv")
    st.download_button("📥 Download Excel", data=open(output_xlsx, "rb").read(),
                       file_name=output_xlsx, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
