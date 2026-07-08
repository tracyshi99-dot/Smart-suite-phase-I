"""
Mario-GEO 数据提取工具
从 SSR Funnel Metrics Sheet 1 CSV 数据中提取 Sheet 2 格式的 GEO + Direct 汇总表。

Run: streamlit run mario_geo.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

st.set_page_config(
    page_title="Mario-GEO 数据工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
.main .block-container { padding-top: 1.2rem; max-width: 1400px; }
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1a2940 0%, #0d1b2a 100%);
    border: 1px solid #2a4a6f; border-radius: 10px; padding: 12px 16px;
}
.stDataFrame { font-size: 0.85rem; }
h3 { margin-top: 0.5rem !important; padding-bottom: 0.3rem !important; border-bottom: 1px solid #2a2a2a; }
.highlight-positive { color: #4caf50; font-weight: bold; }
.highlight-negative { color: #f44336; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# PARSING LOGIC
# ============================================================

def parse_number(val):
    """Parse number from string, handling commas and special cases."""
    if pd.isna(val) or val == "" or val == ".%":
        return np.nan
    val = str(val).strip().replace(",", "").replace("%", "")
    try:
        return float(val)
    except ValueError:
        return np.nan


def find_row_data(df, metrics_name, channel_attr, channel_cat, campaign_rollup, row_type="Actual"):
    """
    Find a specific row in the parsed Sheet 1 data.
    Returns the weekly/monthly data values.
    """
    mask = pd.Series([True] * len(df), index=df.index)

    if metrics_name:
        mask &= df["Metrics Name"].fillna("").str.strip() == metrics_name
    if channel_attr:
        mask &= df["Channel Attributes"].fillna("").str.strip() == channel_attr
    if channel_cat:
        mask &= df["Channel Category"].fillna("").str.strip() == channel_cat
    if campaign_rollup:
        mask &= df["Campaign Channel Rollup"].fillna("").str.strip() == campaign_rollup
    if row_type:
        mask &= df["Row Type"].fillna("").str.strip() == row_type

    filtered = df[mask]
    if filtered.empty:
        return None
    return filtered.iloc[0]


def parse_sheet1_csv(csv_text):
    """
    Parse the Sheet 1 CSV text into a structured DataFrame.
    The CSV has a complex header structure that we need to handle.
    """
    lines = csv_text.strip().split("\n")

    # Find the header row with week labels (WK8, WK9, etc.)
    header_idx = None
    for i, line in enumerate(lines):
        if "WK8" in line or "WK9" in line or "WK10" in line:
            header_idx = i
            break

    if header_idx is None:
        # Try alternative: look for "Metrics Name"
        for i, line in enumerate(lines):
            if "Metrics Name" in line:
                header_idx = i
                break

    if header_idx is None:
        st.error("无法识别表头行，请确认 CSV 格式正确")
        return None

    # Parse using pandas from the header row
    csv_from_header = "\n".join(lines[header_idx:])
    df_raw = pd.read_csv(io.StringIO(csv_from_header), header=0)

    # The first few columns are metadata, rest are data
    # Expected columns: (blank), Metrics Name, Channel Attributes, Channel Category,
    #                   Campaign Channel Rollup, (blank for row type), then weekly data...
    # We need to identify the structure

    # Rename columns for clarity
    cols = df_raw.columns.tolist()

    # Build structured data
    records = []
    current_metrics = ""
    current_channel_attr = ""
    current_channel_cat = ""
    current_campaign_rollup = ""

    for _, row in df_raw.iterrows():
        # Update cascading values (they only appear on first row of group)
        vals = row.values

        # Column mapping based on Sheet 1 structure:
        # Col 0: blank (index)
        # Col 1: Metrics Name (e.g., "Reg Start", "Clean Launch")
        # Col 2: Channel Attributes (e.g., "Organic", "Paid")
        # Col 3: Channel Category (e.g., "CN Website", "NA Website")
        # Col 4: Campaign Channel Rollup (e.g., "Direct", "GEO", "SEO")
        # Col 5: Row Type (e.g., "Actual", "PY A2A", "YoY")
        # Col 6+: Weekly data values

        # Find the metadata columns
        meta_cols = min(6, len(cols))

        # Update cascading fields
        raw_metrics = str(vals[0]).strip() if pd.notna(vals[0]) and str(vals[0]).strip() not in ["nan", ""] else ""
        raw_attr = str(vals[1]).strip() if len(vals) > 1 and pd.notna(vals[1]) and str(vals[1]).strip() not in ["nan", ""] else ""
        raw_cat = str(vals[2]).strip() if len(vals) > 2 and pd.notna(vals[2]) and str(vals[2]).strip() not in ["nan", ""] else ""
        raw_rollup = str(vals[3]).strip() if len(vals) > 3 and pd.notna(vals[3]) and str(vals[3]).strip() not in ["nan", ""] else ""
        raw_type = str(vals[4]).strip() if len(vals) > 4 and pd.notna(vals[4]) and str(vals[4]).strip() not in ["nan", ""] else ""

        if raw_metrics:
            current_metrics = raw_metrics
        if raw_attr:
            current_channel_attr = raw_attr
        if raw_cat:
            current_channel_cat = raw_cat
        if raw_rollup:
            current_campaign_rollup = raw_rollup

        # Skip rows without a row type
        if raw_type not in ["Actual", "PY A2A", "YoY"]:
            continue

        # Extract data values (columns after metadata)
        data_vals = [parse_number(v) for v in vals[5:]]

        record = {
            "Metrics Name": current_metrics,
            "Channel Attributes": current_channel_attr,
            "Channel Category": current_channel_cat,
            "Campaign Channel Rollup": current_campaign_rollup,
            "Row Type": raw_type,
            "data": data_vals,
        }
        records.append(record)

    return records


def extract_monthly_data(row_data, col_mapping):
    """Extract monthly values from a data row using column mapping."""
    if row_data is None:
        return {}
    data = row_data.get("data", [])
    result = {}
    for key, idx in col_mapping.items():
        if idx < len(data):
            result[key] = data[idx]
        else:
            result[key] = np.nan
    return result


def process_sheet1_to_sheet2(records, col_mapping):
    """
    Process parsed Sheet 1 records into Sheet 2 format.
    
    col_mapping: dict mapping output column names to data array indices
    e.g., {"M1": 17, "M2": 18, "M3": 19, "M4": 20, "Q1": 21, "MTD": 15, "QTD": 16, "YTD": 17}
    """

    def get_row(metrics, attr, cat, rollup, row_type="Actual"):
        """Find matching record."""
        for r in records:
            if (r["Metrics Name"] == metrics and
                r["Channel Attributes"] == attr and
                r["Channel Category"] == cat and
                r["Campaign Channel Rollup"] == rollup and
                r["Row Type"] == row_type):
                return r
        return None

    def get_val(record, idx):
        """Get value at index from record's data array."""
        if record is None:
            return np.nan
        data = record.get("data", [])
        if idx < len(data):
            return data[idx]
        return np.nan

    def sum_vals(record_list, idx):
        """Sum values from multiple records at a given index."""
        total = 0
        for r in record_list:
            v = get_val(r, idx)
            if not np.isnan(v):
                total += v
        return total

    # Define the source rows for Sheet 2
    # Regstart section
    regstart_sources = {
        "GEO": {
            "components": [
                ("Reg Start", "Organic", "CN Website", "GEO"),
                ("Reg Start", "Organic", "NA Website", "GEO"),
                ("Reg Start", "Organic", "EU Website", "GEO"),
                ("Reg Start", "Organic", "JP Website", "GEO"),
            ],
            "is_sum": True
        },
        "CN Website (GEO)": ("Reg Start", "Organic", "CN Website", "GEO"),
        "NA Website (GEO)": ("Reg Start", "Organic", "NA Website", "GEO"),
        "EU Website (GEO)": ("Reg Start", "Organic", "EU Website", "GEO"),
        "JP Website (GEO)": ("Reg Start", "Organic", "JP Website", "GEO"),
        "WW Website Direct": {
            "components": [
                ("Reg Start", "Organic", "NA Website", "Direct"),
                ("Reg Start", "Organic", "EU Website", "Direct"),
                ("Reg Start", "Organic", "JP Website", "Direct"),
            ],
            "is_sum": True
        },
        "NA Website (Direct)": ("Reg Start", "Organic", "NA Website", "Direct"),
        "EU Website (Direct)": ("Reg Start", "Organic", "EU Website", "Direct"),
        "JP Website (Direct)": ("Reg Start", "Organic", "JP Website", "Direct"),
    }

    # Clean Launch section
    clean_launch_sources = {
        "GEO": {
            "components": [
                ("Clean Launch", "Organic", "CN Website", "GEO"),
                ("Clean Launch", "Organic", "NA Website", "GEO"),
                ("Clean Launch", "Organic", "EU Website", "GEO"),
                ("Clean Launch", "Organic", "JP Website", "GEO"),
            ],
            "is_sum": True
        },
        "CN Website (GEO)": ("Clean Launch", "Organic", "CN Website", "GEO"),
        "NA Website (GEO)": ("Clean Launch", "Organic", "NA Website", "GEO"),
        "EU Website (GEO)": ("Clean Launch", "Organic", "EU Website", "GEO"),
        "JP Website (GEO)": ("Clean Launch", "Organic", "JP Website", "GEO"),
        "WW Website Direct": {
            "components": [
                ("Clean Launch", "Organic", "NA Website", "Direct"),
                ("Clean Launch", "Organic", "EU Website", "Direct"),
                ("Clean Launch", "Organic", "JP Website", "Direct"),
            ],
            "is_sum": True
        },
        "NA Website (Direct)": ("Clean Launch", "Organic", "NA Website", "Direct"),
        "EU Website (Direct)": ("Clean Launch", "Organic", "EU Website", "Direct"),
        "JP Website (Direct)": ("Clean Launch", "Organic", "JP Website", "Direct"),
    }

    def build_section(sources, row_types=("Actual", "PY A2A")):
        """Build a section of Sheet 2 data."""
        results = []
        for label, source in sources.items():
            for rt in row_types:
                if isinstance(source, dict) and source.get("is_sum"):
                    # Sum multiple components
                    component_records = []
                    for comp in source["components"]:
                        r = get_row(*comp, row_type=rt)
                        if r:
                            component_records.append(r)

                    row_data = {}
                    for col_name, idx in col_mapping.items():
                        row_data[col_name] = sum_vals(component_records, idx)

                    results.append({"Label": label, "Type": rt, **row_data})
                else:
                    # Single source
                    r = get_row(*source, row_type=rt)
                    row_data = {}
                    for col_name, idx in col_mapping.items():
                        v = get_val(r, idx)
                        row_data[col_name] = v
                    results.append({"Label": label, "Type": rt, **row_data})

            # Calculate YoY
            actual_row = results[-2]  # Actual
            py_row = results[-1]  # PY A2A
            yoy_row = {"Label": label, "Type": "YoY"}
            for col_name in col_mapping.keys():
                a = actual_row.get(col_name, np.nan)
                p = py_row.get(col_name, np.nan)
                if pd.notna(a) and pd.notna(p) and p != 0:
                    yoy_row[col_name] = (a - p) / p
                else:
                    yoy_row[col_name] = np.nan
            results.append(yoy_row)

        return results

    regstart_data = build_section(regstart_sources)
    clean_launch_data = build_section(clean_launch_sources)

    # Calculate conversion rates (Clean Launch / Regstart)
    conversion_data = []
    for label in regstart_sources.keys():
        # Find Actual rows
        rs_actual = next((r for r in regstart_data if r["Label"] == label and r["Type"] == "Actual"), None)
        cl_actual = next((r for r in clean_launch_data if r["Label"] == label and r["Type"] == "Actual"), None)

        conv_row = {"Label": label, "Type": "Rate"}
        if rs_actual and cl_actual:
            for col_name in col_mapping.keys():
                rs_val = rs_actual.get(col_name, np.nan)
                cl_val = cl_actual.get(col_name, np.nan)
                if pd.notna(rs_val) and pd.notna(cl_val) and rs_val != 0:
                    conv_row[col_name] = cl_val / rs_val
                else:
                    conv_row[col_name] = np.nan
        conversion_data.append(conv_row)

        # PY conversion
        rs_py = next((r for r in regstart_data if r["Label"] == label and r["Type"] == "PY A2A"), None)
        cl_py = next((r for r in clean_launch_data if r["Label"] == label and r["Type"] == "PY A2A"), None)

        conv_py_row = {"Label": label, "Type": "PY Rate"}
        if rs_py and cl_py:
            for col_name in col_mapping.keys():
                rs_val = rs_py.get(col_name, np.nan)
                cl_val = cl_py.get(col_name, np.nan)
                if pd.notna(rs_val) and pd.notna(cl_val) and rs_val != 0:
                    conv_py_row[col_name] = cl_val / rs_val
                else:
                    conv_py_row[col_name] = np.nan
        conversion_data.append(conv_py_row)

        # BPS change
        bps_row = {"Label": label, "Type": "BPS Change"}
        for col_name in col_mapping.keys():
            curr = conv_row.get(col_name, np.nan)
            prev = conv_py_row.get(col_name, np.nan)
            if pd.notna(curr) and pd.notna(prev):
                bps_row[col_name] = (curr - prev) * 10000  # basis points
            else:
                bps_row[col_name] = np.nan
        conversion_data.append(bps_row)

    return regstart_data, clean_launch_data, conversion_data


# ============================================================
# SMART COLUMN DETECTION
# ============================================================

def detect_columns(first_data_row):
    """
    Detect column positions for Monthly, Quarterly, MTD/QTD/YTD data.
    Based on the standard Sheet 1 layout with weekly columns followed by
    MTD, QTD, YTD, M1, M2, M3, M4, Q1
    """
    # Standard positions (0-indexed from data start):
    # Weeks: 0-14 (WK8 through WK22 = 15 weeks)
    # MTD: 15
    # QTD: 16
    # YTD: 17
    # M1 (Jan): 18
    # M2 (Feb): 19
    # M3 (Mar): 20
    # M4 (Apr): 21
    # Q1: 22
    return {
        "Jan": 18,
        "Feb": 19,
        "Mar": 20,
        "Apr": 21,
        "May (MTD)": 15,
        "Q1": 22,
        "QTD": 16,
        "YTD": 17,
    }


# ============================================================
# DISPLAY FUNCTIONS
# ============================================================

def format_number(val, is_pct=False, is_bps=False):
    """Format a number for display."""
    if pd.isna(val):
        return "-"
    if is_bps:
        return f"{val:+,.0f} bps"
    if is_pct:
        return f"{val:+.1%}"
    if abs(val) >= 1000:
        return f"{val:,.0f}"
    if val == int(val):
        return f"{int(val)}"
    return f"{val:.1f}"


def create_display_df(data, col_names, section_type="absolute"):
    """Create a formatted display DataFrame."""
    rows = []
    for item in data:
        row = {"#": "", "Channel": item["Label"], " ": item["Type"]}
        for col in col_names:
            val = item.get(col, np.nan)
            if item["Type"] == "YoY":
                row[col] = format_number(val, is_pct=True)
            elif item["Type"] == "BPS Change":
                row[col] = format_number(val, is_bps=True)
            elif item["Type"] in ["Rate", "PY Rate"]:
                row[col] = f"{val:.1%}" if pd.notna(val) else "-"
            else:
                row[col] = format_number(val)
        rows.append(row)

    df = pd.DataFrame(rows)

    # Add row numbers
    counter = 0
    for i in range(len(df)):
        if df.iloc[i][" "] == "Actual":
            counter += 1
            df.iloc[i, 0] = str(counter)

    return df


# ============================================================
# MAIN UI
# ============================================================

from pathlib import Path
import plotly.graph_objects as go

BASE_PATH = Path(__file__).parent.parent
METRICS_PATH = BASE_PATH / "output" / "metrics"

st.title("📊 Mario-GEO 数据提取工具")
st.caption("从 SSR Funnel Metrics (Sheet 1) 提取 GEO + Direct 汇总数据 (Sheet 2 格式)")

# ============================================================
# AUTO-LOAD: Sheet2 format data (Y2026 vs Y2025 with YoY)
# ============================================================
_s2_rs_file = METRICS_PATH / "geo_sheet2_regstart.csv"
_s2_cl_file = METRICS_PATH / "geo_sheet2_cleanlaunch.csv"
_s2_conv_file = METRICS_PATH / "geo_sheet2_conversion.csv"

if _s2_rs_file.exists() and _s2_cl_file.exists() and _s2_conv_file.exists():
    _s2_rs = pd.read_csv(_s2_rs_file, encoding="utf-8-sig")
    _s2_cl = pd.read_csv(_s2_cl_file, encoding="utf-8-sig")
    _s2_conv = pd.read_csv(_s2_conv_file, encoding="utf-8-sig")

    st.divider()
    st.subheader("📊 Sheet 2 — GEO + Direct Summary (Y2026 vs Y2025)")

    # KPI Row
    _rs_ytd_2026 = _s2_rs[(_s2_rs["Channel"] == "GEO") & (_s2_rs["Type"] == "Actual")]
    _rs_direct_ytd = _s2_rs[(_s2_rs["Channel"] == "WW Website Direct") & (_s2_rs["Type"] == "Actual")]
    _cl_ytd_2026 = _s2_cl[(_s2_cl["Channel"] == "GEO") & (_s2_cl["Type"] == "Actual")]
    _cl_direct_ytd = _s2_cl[(_s2_cl["Channel"] == "WW Website Direct") & (_s2_cl["Type"] == "Actual")]

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        geo_rs = int(_rs_ytd_2026.iloc[0]["YTD"]) if not _rs_ytd_2026.empty and pd.notna(_rs_ytd_2026.iloc[0]["YTD"]) else 0
        geo_yoy = _s2_rs[(_s2_rs["Channel"] == "GEO") & (_s2_rs["Type"] == "YoY")]
        geo_yoy_val = geo_yoy.iloc[0]["YTD"] if not geo_yoy.empty and pd.notna(geo_yoy.iloc[0]["YTD"]) else 0
        st.metric("GEO Regstart YTD", f"{geo_rs:,}", f"+{geo_yoy_val:.0%}")
    with k2:
        direct_rs = int(_rs_direct_ytd.iloc[0]["YTD"]) if not _rs_direct_ytd.empty and pd.notna(_rs_direct_ytd.iloc[0]["YTD"]) else 0
        direct_yoy = _s2_rs[(_s2_rs["Channel"] == "WW Website Direct") & (_s2_rs["Type"] == "YoY")]
        direct_yoy_val = direct_yoy.iloc[0]["YTD"] if not direct_yoy.empty and pd.notna(direct_yoy.iloc[0]["YTD"]) else 0
        st.metric("WW Direct Regstart YTD", f"{direct_rs:,}", f"+{direct_yoy_val:.0%}")
    with k3:
        cl_total = 0
        if not _cl_ytd_2026.empty and pd.notna(_cl_ytd_2026.iloc[0]["YTD"]):
            cl_total += int(_cl_ytd_2026.iloc[0]["YTD"])
        if not _cl_direct_ytd.empty and pd.notna(_cl_direct_ytd.iloc[0]["YTD"]):
            cl_total += int(_cl_direct_ytd.iloc[0]["YTD"])
        st.metric("Clean Launch Total YTD", f"{cl_total:,}")
    with k4:
        total_rs = geo_rs + direct_rs
        conv_rate = cl_total / total_rs if total_rs > 0 else 0
        st.metric("Conversion Rate", f"{conv_rate:.1%}")

    # Tabs matching Sheet2 sections
    _s2_tab_rs, _s2_tab_cl, _s2_tab_conv, _s2_tab_trend = st.tabs([
        "📈 Regstart (#1-9)", "🚀 Clean Launch (#10-18)", "📊 Conversion (#19-27)", "📉 Trends"
    ])

    _period_cols = ["Jan", "Feb", "Mar", "Apr", "May", "Q1", "Q2", "YTD"]

    def _fmt_sheet2(df, is_rate=False):
        """Format Sheet2 data for display."""
        display = df[["#", "Channel", "Year", "Type"] + [c for c in _period_cols if c in df.columns]].copy()
        for col in _period_cols:
            if col in display.columns:
                def fmt_val(row):
                    val = row[col]
                    if pd.isna(val):
                        return "-"
                    tp = row["Type"]
                    if tp == "YoY":
                        return f"{val:+.1%}"
                    elif tp == "Rate":
                        return f"{val:.1%}"
                    elif tp == "BPS Change":
                        return f"{int(val):+,} bps"
                    else:
                        if abs(val) >= 1:
                            return f"{int(val):,}"
                        return f"{val:.1%}" if abs(val) < 1 else str(val)
                display[col] = display.apply(fmt_val, axis=1)
        return display

    with _s2_tab_rs:
        st.markdown("**Regstart — Y2026 Actual / Y2025 PY / YoY**")
        st.dataframe(_fmt_sheet2(_s2_rs), use_container_width=True, hide_index=True, height=700)

    with _s2_tab_cl:
        st.markdown("**Clean Launch — Y2026 Actual / Y2025 PY / YoY**")
        st.dataframe(_fmt_sheet2(_s2_cl), use_container_width=True, hide_index=True, height=700)

    with _s2_tab_conv:
        st.markdown("**Regstart → Clean Launch Conversion — Y2026 Rate / Y2025 Rate / BPS Change**")
        st.dataframe(_fmt_sheet2(_s2_conv, is_rate=True), use_container_width=True, hide_index=True, height=700)

    with _s2_tab_trend:
        st.markdown("**Monthly Trend — Regstart (Y2026 vs Y2025)**")
        _mlabels = ["Jan", "Feb", "Mar", "Apr", "May"]

        # GEO + WW Direct combined
        fig1 = go.Figure()
        for label, color, dash in [("GEO", "#fbbf24", None), ("WW Website Direct", "#4a9eff", None)]:
            row = _s2_rs[(_s2_rs["Channel"] == label) & (_s2_rs["Type"] == "Actual")]
            if not row.empty:
                vals = [float(row.iloc[0][m]) if pd.notna(row.iloc[0][m]) else 0 for m in _mlabels]
                fig1.add_trace(go.Scatter(x=_mlabels, y=vals, mode="lines+markers",
                                          name=f"{label} (2026)", line=dict(color=color, width=2)))
            row_py = _s2_rs[(_s2_rs["Channel"] == label) & (_s2_rs["Type"] == "PY")]
            if not row_py.empty:
                vals_py = [float(row_py.iloc[0][m]) if pd.notna(row_py.iloc[0][m]) else 0 for m in _mlabels]
                fig1.add_trace(go.Scatter(x=_mlabels, y=vals_py, mode="lines+markers",
                                          name=f"{label} (2025)", line=dict(color=color, width=1, dash="dash")))
        fig1.update_layout(height=380, margin=dict(l=0, r=0, t=30, b=0), yaxis_title="Reg Starts",
                           legend=dict(orientation="h", y=-0.2), hovermode="x unified")
        st.plotly_chart(fig1, use_container_width=True)

        # Clean Launch trend
        st.markdown("**Monthly Trend — Clean Launch (Y2026 vs Y2025)**")
        fig2 = go.Figure()
        for label, color in [("GEO", "#22c55e"), ("WW Website Direct", "#06b6d4")]:
            row = _s2_cl[(_s2_cl["Channel"] == label) & (_s2_cl["Type"] == "Actual")]
            if not row.empty:
                vals = [float(row.iloc[0][m]) if pd.notna(row.iloc[0][m]) else 0 for m in _mlabels]
                fig2.add_trace(go.Scatter(x=_mlabels, y=vals, mode="lines+markers",
                                          name=f"{label} (2026)", line=dict(color=color, width=2)))
            row_py = _s2_cl[(_s2_cl["Channel"] == label) & (_s2_cl["Type"] == "PY")]
            if not row_py.empty:
                vals_py = [float(row_py.iloc[0][m]) if pd.notna(row_py.iloc[0][m]) else 0 for m in _mlabels]
                fig2.add_trace(go.Scatter(x=_mlabels, y=vals_py, mode="lines+markers",
                                          name=f"{label} (2025)", line=dict(color=color, width=1, dash="dash")))
        fig2.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0), yaxis_title="Clean Launches",
                           legend=dict(orientation="h", y=-0.2), hovermode="x unified")
        st.plotly_chart(fig2, use_container_width=True)

        # Conversion Rate trend
        st.markdown("**Monthly Trend — Conversion Rate (Y2026 vs Y2025)**")
        fig3 = go.Figure()
        for label, color in [("GEO", "#fbbf24"), ("WW Website Direct", "#4a9eff"),
                             ("NA Website (Direct)", "#a78bfa"), ("EU Website (Direct)", "#f87171"),
                             ("JP Website (Direct)", "#22c55e")]:
            row = _s2_conv[(_s2_conv["Channel"] == label) & (_s2_conv["Type"] == "Rate") & (_s2_conv["Year"] == "Y2026")]
            if not row.empty:
                vals = [float(row.iloc[0][m]) * 100 if pd.notna(row.iloc[0][m]) else None for m in _mlabels]
                fig3.add_trace(go.Scatter(x=_mlabels, y=vals, mode="lines+markers",
                                          name=f"{label} (2026)", line=dict(color=color, width=2)))
            row_py = _s2_conv[(_s2_conv["Channel"] == label) & (_s2_conv["Type"] == "Rate") & (_s2_conv["Year"] == "Y2025")]
            if not row_py.empty:
                vals_py = [float(row_py.iloc[0][m]) * 100 if pd.notna(row_py.iloc[0][m]) else None for m in _mlabels]
                fig3.add_trace(go.Scatter(x=_mlabels, y=vals_py, mode="lines+markers",
                                          name=f"{label} (2025)", line=dict(color=color, width=1, dash="dash")))
        fig3.update_layout(height=380, margin=dict(l=0, r=0, t=30, b=0), yaxis_title="Conversion %",
                           legend=dict(orientation="h", y=-0.25), hovermode="x unified")
        st.plotly_chart(fig3, use_container_width=True)

    st.divider()

st.divider()

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ 设置")
    st.markdown("""
    **使用说明：**
    1. 从 QuickSight 导出 Sheet 1 的 CSV 数据
    2. 上传到此工具
    3. 自动生成 Sheet 2 格式的汇总表
    4. 可下载结果 CSV
    """)

    st.divider()
    st.markdown("**数据口径：**")
    st.markdown("""
    - **GEO**: Organic → 各 Website → GEO
    - **WW Direct**: Organic → NA/EU/JP Website → Direct
    - **转化率**: Clean Launch / Reg Start
    - **YoY**: (Actual - PY) / PY
    - **BPS**: (当年转化率 - 去年转化率) × 10,000
    """)

# --- Upload ---
st.subheader("📤 上传 Sheet 1 数据")

upload_method = st.radio(
    "数据输入方式",
    ["📋 粘贴 CSV 文本", "📁 上传 CSV 文件"],
    horizontal=True,
)

csv_data = None

if upload_method == "📋 粘贴 CSV 文本":
    csv_text = st.text_area(
        "粘贴 Sheet 1 的 CSV 数据（从 Excel 复制 tab-separated 也可以）",
        height=200,
        placeholder="Metrics Name\tChannel Attributes\tChannel Category\t...\nReg Start\tOrganic\tCN Website\t...",
    )
    if csv_text.strip():
        csv_data = csv_text

elif upload_method == "📁 上传 CSV 文件":
    uploaded_file = st.file_uploader("选择 CSV 文件", type=["csv", "tsv", "txt"])
    if uploaded_file:
        csv_data = uploaded_file.read().decode("utf-8-sig")

# --- Process ---
if csv_data:
    with st.spinner("正在解析数据..."):
        records = parse_sheet1_csv(csv_data)

    if records:
        st.success(f"✅ 成功解析 {len(records)} 行数据")

        # Detect column mapping
        col_mapping = detect_columns(records[0]["data"] if records else [])

        # Show detected mapping
        with st.expander("🔧 列映射（可调整）", expanded=False):
            st.json(col_mapping)
            st.caption("如果数据列数不同，可在此处调整索引位置")

        # Process data
        regstart_data, clean_launch_data, conversion_data = process_sheet1_to_sheet2(records, col_mapping)

        col_names = list(col_mapping.keys())

        # --- Display Results ---
        st.divider()

        # Section 1: Regstart
        st.subheader("📈 Regstart")
        df_regstart = create_display_df(regstart_data, col_names)
        st.dataframe(df_regstart, use_container_width=True, hide_index=True)

        # Section 2: Clean Launch
        st.subheader("🚀 Clean Launch")
        df_clean_launch = create_display_df(clean_launch_data, col_names)
        st.dataframe(df_clean_launch, use_container_width=True, hide_index=True)

        # Section 3: Conversion Rate
        st.subheader("📊 Regstart to Clean Launch 转化率")
        df_conversion = create_display_df(conversion_data, col_names, section_type="rate")
        st.dataframe(df_conversion, use_container_width=True, hide_index=True)

        # --- Summary KPIs ---
        st.divider()
        st.subheader("🎯 关键指标一览")

        # Find key values for KPI display
        geo_actual = next((r for r in regstart_data if r["Label"] == "GEO" and r["Type"] == "Actual"), {})
        geo_yoy = next((r for r in regstart_data if r["Label"] == "GEO" and r["Type"] == "YoY"), {})
        direct_actual = next((r for r in regstart_data if r["Label"] == "WW Website Direct" and r["Type"] == "Actual"), {})
        direct_yoy = next((r for r in regstart_data if r["Label"] == "WW Website Direct" and r["Type"] == "YoY"), {})

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            ytd_geo = geo_actual.get("YTD", 0)
            ytd_geo_yoy = geo_yoy.get("YTD", 0)
            st.metric(
                "GEO Total (YTD)",
                format_number(ytd_geo),
                f"{ytd_geo_yoy:+.1%}" if pd.notna(ytd_geo_yoy) else "N/A"
            )
        with c2:
            ytd_direct = direct_actual.get("YTD", 0)
            ytd_direct_yoy = direct_yoy.get("YTD", 0)
            st.metric(
                "WW Direct (YTD)",
                format_number(ytd_direct),
                f"{ytd_direct_yoy:+.1%}" if pd.notna(ytd_direct_yoy) else "N/A"
            )
        with c3:
            total = (ytd_geo or 0) + (ytd_direct or 0)
            st.metric("GEO + Direct Total (YTD)", format_number(total))
        with c4:
            cl_geo = next((r for r in clean_launch_data if r["Label"] == "GEO" and r["Type"] == "Actual"), {})
            cl_direct = next((r for r in clean_launch_data if r["Label"] == "WW Website Direct" and r["Type"] == "Actual"), {})
            cl_total = (cl_geo.get("YTD", 0) or 0) + (cl_direct.get("YTD", 0) or 0)
            st.metric("Clean Launch Total (YTD)", format_number(cl_total))

        # --- Download ---
        st.divider()
        st.subheader("📥 下载结果")

        col_dl1, col_dl2, col_dl3 = st.columns(3)

        with col_dl1:
            csv_regstart = df_regstart.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                "⬇️ Regstart CSV",
                csv_regstart,
                file_name=f"mario_geo_regstart_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

        with col_dl2:
            csv_cl = df_clean_launch.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                "⬇️ Clean Launch CSV",
                csv_cl,
                file_name=f"mario_geo_clean_launch_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

        with col_dl3:
            csv_conv = df_conversion.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                "⬇️ 转化率 CSV",
                csv_conv,
                file_name=f"mario_geo_conversion_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

        # Combined download
        st.markdown("---")
        # Build combined Excel
        output_buffer = io.BytesIO()
        with pd.ExcelWriter(output_buffer, engine="openpyxl") as writer:
            df_regstart.to_excel(writer, sheet_name="Regstart", index=False)
            df_clean_launch.to_excel(writer, sheet_name="Clean Launch", index=False)
            df_conversion.to_excel(writer, sheet_name="Conversion Rate", index=False)

        st.download_button(
            "📊 下载完整 Excel（含全部 3 个 Sheet）",
            output_buffer.getvalue(),
            file_name=f"mario_geo_full_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
        )

    else:
        st.error("❌ 解析失败，请检查数据格式")

else:
    # Show example / instructions
    st.info("👆 请上传或粘贴 Sheet 1 的 CSV 数据开始处理")

    with st.expander("📖 数据格式说明", expanded=True):
        st.markdown("""
        **支持的输入格式：**
        - 从 Excel 直接复制粘贴（Tab-separated）
        - 导出的 CSV 文件（逗号分隔）

        **必须包含的列：**
        - Metrics Name（如 Reg Start, Clean Launch）
        - Channel Attributes（如 Organic, Paid）
        - Channel Category（如 CN Website, NA Website, EU Website, JP Website）
        - Campaign Channel Rollup（如 Direct, GEO, SEO）
        - 数据行类型：Actual, PY A2A, YoY

        **Sheet 2 输出的行映射：**

        | # | Sheet 2 行 | Sheet 1 来源 |
        |---|---|---|
        | 1 | GEO | Organic → CN+NA+EU+JP Website → GEO 求和 |
        | 2 | CN Website | Organic → CN Website → GEO |
        | 3 | NA Website | Organic → NA Website → GEO |
        | 4 | EU Website | Organic → EU Website → GEO |
        | 5 | JP Website | Organic → JP Website → GEO |
        | 6 | WW Website Direct | Organic → NA+EU+JP Website → Direct 求和 |
        | 7 | NA Website | Organic → NA Website → Direct |
        | 8 | EU Website | Organic → EU Website → Direct |
        | 9 | JP Website | Organic → JP Website → Direct |
        """)

    with st.expander("📋 示例数据", expanded=False):
        st.code("""Metrics Name\tChannel Attributes\tChannel Category\tCampaign Channel Rollup\t\tWK8\tWK9\t...\tMTD\tQTD\tYTD\tM1\tM2\tM3\tM4\tQ1
Reg Start\tOrganic\tCN Website\tGEO\tActual\t2\t35\t...\t159\t323\t653\t89\t65\t165\t164\t319
\t\t\t\tPY A2A\t4\t5\t...\t29\t59\t121\t13\t13\t36\t30\t62
\t\t\t\tYoY\t-50.0%\t600.0%\t...\t448.2%\t447.4%\t439.7%\t584.6%\t400.0%\t358.3%\t446.7%\t414.4%""",
        language=None)
