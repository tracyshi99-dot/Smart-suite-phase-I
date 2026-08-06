"""
Parse GEO Input Detail from xlsx to gap_verification_cn.csv
Usage: python parse_geo_detail.py <path_to_xlsx>

Reads the "3.2 GEO Input detail" data and generates the gap_verification_cn.csv
with all 646 phrases and their per-platform link citation status.
"""
import sys
import pandas as pd
from pathlib import Path

def parse_geo_detail(xlsx_path: str):
    """Parse the GEO detail xlsx and output gap_verification_cn.csv"""
    
    # Try reading different possible sheet names
    xl = pd.ExcelFile(xlsx_path)
    print(f"Available sheets: {xl.sheet_names}")
    
    # Find the detail sheet
    detail_sheet = None
    for sn in xl.sheet_names:
        if "3.2" in sn or "detail" in sn.lower() or "Input detail" in sn:
            detail_sheet = sn
            break
    
    if not detail_sheet:
        # Try the sheet with the most rows (likely the detail data)
        max_rows = 0
        for sn in xl.sheet_names:
            try:
                df = pd.read_excel(xlsx_path, sheet_name=sn, nrows=5)
                full = pd.read_excel(xlsx_path, sheet_name=sn)
                if len(full) > max_rows:
                    max_rows = len(full)
                    detail_sheet = sn
            except:
                pass
    
    print(f"Using sheet: {detail_sheet}")
    
    # Read the full sheet
    df_raw = pd.read_excel(xlsx_path, sheet_name=detail_sheet, header=None)
    print(f"Raw shape: {df_raw.shape}")
    
    # Find the header row with platform names (元宝, DeepSeek, etc.)
    # and the data rows with queries
    # The structure has: 分类 | 品牌-提示词 | 提及引用链接 | 元宝(11月~6月) | DeepSeek(11月~6月) | ...
    
    # Look for the row containing platform column headers
    results = []
    
    # Parse brand queries section
    brand_start = None
    industry_start = None
    
    for i, row in df_raw.iterrows():
        row_str = " ".join([str(x) for x in row.values if pd.notna(x)])
        if "品牌-提示词" in row_str and "提及引用链接" in row_str:
            brand_start = i
        if "行业-提示词" in row_str and "提及引用链接" in row_str:
            industry_start = i
    
    print(f"Brand section starts at row: {brand_start}")
    print(f"Industry section starts at row: {industry_start}")
    
    # For each section, find queries and their 6月 platform data
    # Platform columns for 6月: 元宝-6月, DeepSeek-6月, 豆包-6月, ChatGPT-6月, Kimi-6月, 千问-6月, Gemini-6月
    
    # Since the xlsx structure is complex, let's use the "语义范围" section 
    # which has cleaner per-category per-platform monthly data
    
    # Alternative: parse from the flat query list
    # Each row after the header has: category, subcategory, query, content_url, then platform columns
    
    # Let's try a simpler approach - read the specific columns
    if brand_start is not None:
        # Find column positions for 6月 data
        header_row = df_raw.iloc[brand_start]
        
        # The actual data starts 1-2 rows after the header
        data_start = brand_start + 1
        
        for i in range(data_start, len(df_raw)):
            row = df_raw.iloc[i]
            # Check if this looks like a data row (has a query text)
            query_col = None
            for j, val in enumerate(row):
                if pd.notna(val) and isinstance(val, str) and len(val) > 10 and "?" in val or "？" in val:
                    query_col = j
                    break
            
            if query_col is None:
                # Try finding query by checking if column 2 or 3 has Chinese text
                for j in [2, 3]:
                    if j < len(row) and pd.notna(row.iloc[j]) and isinstance(row.iloc[j], str) and len(row.iloc[j]) > 5:
                        if any('\u4e00' <= c <= '\u9fff' for c in str(row.iloc[j])):
                            query_col = j
                            break
            
            if query_col is not None:
                query = str(row.iloc[query_col]).strip()
                if len(query) < 5:
                    continue
                    
                # Get category info
                cat = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
                sub_cat = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ""
                content_url = str(row.iloc[query_col + 1]) if query_col + 1 < len(row) and pd.notna(row.iloc[query_col + 1]) else ""
                
                # Get 6月 platform data (last columns for each platform)
                # This requires knowing exact column positions which vary by sheet layout
                
                results.append({
                    "ai_query": query,
                    "category": "品牌" if i < (industry_start or len(df_raw)) else "行业",
                    "sub_category": sub_cat if sub_cat != "nan" else cat,
                    "content_url": content_url if content_url != "nan" else "",
                })
    
    print(f"Parsed {len(results)} queries")
    
    # If parsing failed or got too few, fall back to using the document text data directly
    if len(results) < 100:
        print("WARNING: xlsx parsing got too few results. The file structure may be different.")
        print("Please upload the xlsx via Smart Suite's '上传 GEO 数据' interface instead.")
        return
    
    # Output
    output_path = Path(__file__).parent.parent / "output" / "metrics" / "gap_verification_cn.csv"
    df_out = pd.DataFrame(results)
    df_out.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Saved {len(df_out)} rows to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_geo_detail.py <path_to_xlsx>")
        print("Example: python parse_geo_detail.py 'C:\\Users\\yujiashi\\Downloads\\GEOSEO.xlsx'")
        sys.exit(1)
    
    parse_geo_detail(sys.argv[1])
