"""
Smart Suite — POC Manual Review Interface
独立审核界面，POC 通过 ?reviewer=name 访问，只看到分配给自己的待审核内容
Run: streamlit run app_review.py --server.port 8502
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

# --- Config ---
BASE_PATH = Path(__file__).parent.parent
OUTPUT_PATH = BASE_PATH / "output"
REVIEW_PATH = OUTPUT_PATH / "review"
REVIEW_PATH.mkdir(parents=True, exist_ok=True)

# Review queue file
REVIEW_QUEUE = REVIEW_PATH / "review_queue.csv"
REVIEW_LOG = REVIEW_PATH / "review_log.csv"

st.set_page_config(
    page_title="Smart Suite — Content Review",
    page_icon="📋",
    layout="wide",
)

# --- Custom CSS matching main app ---
st.markdown("""
<style>
.main .block-container { padding-top: 1.2rem; }
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1a1d2e 0%, #12131a 100%);
    border: 1px solid #2a2f4a; border-radius: 10px; padding: 12px 16px;
}
</style>
""", unsafe_allow_html=True)

# --- POC Mapping ---
POC_CATEGORIES = {
    "murphy": [19],
    "joyce": [2, 3, 4, 5, 6, 7, 9, 10, 14, 15, 20, 29],
    "eva_zheng": [21, 23, 24, 25],
    "tianran": [16],
    "hanhong": [17],
    "grace_yan": [18],
    "jiayu": [11, 12],
    "huang_shadie": [22],
    "tina_feng": [26, 27, 31, 32, 33, 34, 35],
    "aki": [30],
}

# Categories that require manual review (Critical 5)
MANUAL_REVIEW_CATEGORIES = [19, 20, 21, 23, 24, 25]

CATEGORY_NAMES = {
    19: "新手怎么注册亚马逊", 20: "亚马逊开店成本费用详解",
    21: "开店审核常见问题解答", 23: "欧洲增值税VAT介绍",
    24: "其他站点税务要求", 25: "合规政策及操作流程",
}


def load_review_queue():
    """Load or create review queue. Handles legacy CSV format from other pipelines."""
    EXPECTED_COLS = [
        "content_id", "category_id", "category_name", "title", "content",
        "assigned_to", "status", "reviewer_notes", "submitted_at", "reviewed_at"
    ]
    if REVIEW_QUEUE.exists():
        df = pd.read_csv(REVIEW_QUEUE, encoding="utf-8-sig")
        # If already in expected format, return as-is
        if "assigned_to" in df.columns and "status" in df.columns:
            return df
        # Legacy format from 智优 pipeline (has needs_poc_review, poc_approved, etc.)
        # Convert to expected format
        if "needs_poc_review" in df.columns or "optimized_content" in df.columns:
            converted_rows = []
            for _, row in df.iterrows():
                # Determine category from keyword_id (e.g. KW_019 → 19)
                cat_num = 0
                kw_id = str(row.get("keyword_id", ""))
                if "_" in kw_id:
                    try:
                        cat_num = int(kw_id.split("_")[1])
                    except (ValueError, IndexError):
                        cat_num = 0
                # Determine assigned POC
                assigned = ""
                for poc, cats in POC_CATEGORIES.items():
                    if cat_num in cats:
                        assigned = poc
                        break
                if not assigned:
                    assigned = "yujiashi"
                # Map status
                poc_approved = row.get("poc_approved", False)
                needs_review = row.get("needs_poc_review", True)
                if poc_approved:
                    status = "APPROVED"
                elif not needs_review:
                    status = "APPROVED"
                else:
                    status = "PENDING"
                # Build converted row
                title = str(row.get("optimized_title", row.get("original_title", row.get("ai_query", ""))))
                content = str(row.get("optimized_content", row.get("content_draft", "")))
                converted_rows.append({
                    "content_id": str(row.get("content_id", "")),
                    "category_id": cat_num,
                    "category_name": CATEGORY_NAMES.get(cat_num, f"Category {cat_num}"),
                    "title": title,
                    "content": content[:5000],
                    "assigned_to": assigned,
                    "status": status,
                    "reviewer_notes": "",
                    "submitted_at": str(row.get("updated_at", "")),
                    "reviewed_at": "",
                })
            if converted_rows:
                return pd.DataFrame(converted_rows)
        # Fallback: return empty with expected columns
        return pd.DataFrame(columns=EXPECTED_COLS)
    return pd.DataFrame(columns=EXPECTED_COLS)


def save_review_queue(df):
    """Save review queue."""
    df.to_csv(REVIEW_QUEUE, index=False, encoding="utf-8-sig")


def log_review_action(content_id, reviewer, action, notes=""):
    """Log review actions."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "content_id": content_id,
        "reviewer": reviewer,
        "action": action,
        "notes": notes,
    }
    if REVIEW_LOG.exists():
        df = pd.read_csv(REVIEW_LOG, encoding="utf-8-sig")
    else:
        df = pd.DataFrame(columns=entry.keys())
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(REVIEW_LOG, index=False, encoding="utf-8-sig")


def submit_for_review(content_id, category_id, title, content, assigned_to):
    """Submit content to review queue (called by 智优 pipeline)."""
    df = load_review_queue()
    new_row = {
        "content_id": content_id,
        "category_id": category_id,
        "category_name": CATEGORY_NAMES.get(category_id, f"Category {category_id}"),
        "title": title,
        "content": content,
        "assigned_to": assigned_to,
        "status": "PENDING",
        "reviewer_notes": "",
        "submitted_at": datetime.now().isoformat(),
        "reviewed_at": "",
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_review_queue(df)
    return True


# --- Main UI ---
# Get reviewer from URL params
qp = st.query_params
reviewer = qp.get("reviewer", "").lower().replace(" ", "_")

# Header
st.markdown("""
<div style="text-align:center;padding:16px 0 8px;">
    <h1 style="font-size:28px;font-weight:800;color:#e91e63;margin:0;">📋 Content Review Portal</h1>
    <p style="color:#8892b0;font-size:14px;">Smart Suite — Manual Review Interface</p>
</div>
""", unsafe_allow_html=True)

with st.expander("ℹ️ What is this? What do I need to do?", expanded=False):
    st.markdown("""
**What:** This is the content review portal for Critical-5 category articles (registration, fees, tax, compliance topics).

**Why you're here:** These topics are high-sensitivity and require human expert verification before publishing. AI has already:
1. Generated the content (智造)
2. Scored and optimized it (智优)
3. Passed compliance check

**What you need to do:**
1. Review the content for factual accuracy
2. Edit if needed (you can directly modify the text)
3. Click **✅ Approve** if ready to publish, or **❌ Reject** if it needs more work
4. Add notes explaining your decision

**After you approve:** Content automatically proceeds to the publishing pipeline (智布 → 智传).
""")

if not reviewer:
    # Show overview of all pending reviews + POC assignment
    df_all = load_review_queue()
    df_pending_all = df_all[df_all["status"] == "PENDING"] if not df_all.empty and "status" in df_all.columns else pd.DataFrame()

    if not df_pending_all.empty:
        st.markdown("### 📋 All Pending Reviews")
        st.caption(f"Total: {len(df_pending_all)} articles awaiting review")
        show_cols = [c for c in ["title", "category_name", "assigned_to", "submitted_at"] if c in df_pending_all.columns]
        if show_cols:
            st.dataframe(df_pending_all[show_cols], use_container_width=True, hide_index=True)
    else:
        st.success("✅ No pending reviews across all POCs!")

    st.divider()

    # Login input
    st.markdown("### 🔑 Enter your reviewer ID to start reviewing")
    login_id = st.text_input("Reviewer ID" , placeholder="e.g. joyce, murphy, eva_zheng", key="reviewer_login")
    if login_id:
        st.query_params["reviewer"] = login_id.strip().lower().replace(" ", "_")
        st.rerun()

    st.divider()
    st.markdown("**Available reviewers:**")
    for name in sorted(POC_CATEGORIES.keys()):
        cats = POC_CATEGORIES[name]
        manual_cats = [c for c in cats if c in MANUAL_REVIEW_CATEGORIES]
        if manual_cats:
            cat_names = [CATEGORY_NAMES.get(c, f"#{c}") for c in manual_cats]
            st.markdown(f"- **{name}**: {', '.join(cat_names)}")
    st.stop()

# Show reviewer's queue
st.markdown(f"### Welcome, **{reviewer}**")
st.caption(f"Reviewing Critical-5 categories: {[CATEGORY_NAMES.get(c, c) for c in POC_CATEGORIES.get(reviewer, []) if c in MANUAL_REVIEW_CATEGORIES]}")

df_queue = load_review_queue()

# Filter for this reviewer
df_mine = df_queue[df_queue["assigned_to"].str.lower().str.replace(" ", "_") == reviewer].copy()

if df_mine.empty:
    st.success("✅ No pending reviews! All caught up.")
    st.caption("When 智造 produces Critical-5 content, it will appear here for your review.")
    st.stop()

# Stats
col1, col2, col3 = st.columns(3)
pending = len(df_mine[df_mine["status"] == "PENDING"])
approved = len(df_mine[df_mine["status"] == "APPROVED"])
rejected = len(df_mine[df_mine["status"] == "REJECTED"])
col1.metric("Pending", pending)
col2.metric("Approved", approved)
col3.metric("Rejected", rejected)

st.divider()

# Show pending items
df_pending = df_mine[df_mine["status"] == "PENDING"]

if df_pending.empty:
    st.success("✅ No pending reviews!")
else:
    st.subheader(f"📝 Pending Reviews ({len(df_pending)})")

    for idx, row in df_pending.iterrows():
        with st.expander(f"📄 {row['title']} — Category: {row['category_name']}", expanded=True):
            st.caption(f"Content ID: {row['content_id']} | Submitted: {row['submitted_at']}")

            # Show content (editable)
            edited_content = st.text_area(
                "Content (edit if needed):",
                value=row["content"],
                height=300,
                key=f"content_{idx}"
            )

            # Reviewer notes
            notes = st.text_input("Notes (optional):", key=f"notes_{idx}")

            # Action buttons
            col_a, col_r, col_s = st.columns([1, 1, 3])
            with col_a:
                if st.button("✅ Approve", key=f"approve_{idx}", type="primary"):
                    # Ensure string columns don't have float64 dtype issues
                    for str_col in ["status", "reviewer_notes", "reviewed_at", "content"]:
                        if str_col in df_queue.columns:
                            df_queue[str_col] = df_queue[str_col].astype(str).replace("nan", "")
                    df_queue.loc[idx, "status"] = "APPROVED"
                    df_queue.loc[idx, "content"] = edited_content
                    df_queue.loc[idx, "reviewer_notes"] = notes if notes else ""
                    df_queue.loc[idx, "reviewed_at"] = datetime.now().isoformat()
                    save_review_queue(df_queue)
                    log_review_action(row["content_id"], reviewer, "APPROVED", notes)
                    st.toast("✅ Approved!")
                    st.rerun()
            with col_r:
                if st.button("❌ Reject", key=f"reject_{idx}"):
                    for str_col in ["status", "reviewer_notes", "reviewed_at"]:
                        if str_col in df_queue.columns:
                            df_queue[str_col] = df_queue[str_col].astype(str).replace("nan", "")
                    df_queue.loc[idx, "status"] = "REJECTED"
                    df_queue.loc[idx, "reviewer_notes"] = notes if notes else ""
                    df_queue.loc[idx, "reviewed_at"] = datetime.now().isoformat()
                    save_review_queue(df_queue)
                    log_review_action(row["content_id"], reviewer, "REJECTED", notes)
                    st.toast("❌ Rejected")
                    st.rerun()

st.divider()

# Show history
with st.expander("📜 Review History"):
    df_done = df_mine[df_mine["status"].isin(["APPROVED", "REJECTED"])]
    if not df_done.empty:
        st.dataframe(
            df_done[["title", "category_name", "status", "reviewer_notes", "reviewed_at"]],
            use_container_width=True, hide_index=True
        )
    else:
        st.caption("No review history yet.")

# --- Admin: Submit test content (for testing) ---
with st.expander("🔧 Admin: Submit Test Content"):
    st.caption("For testing — simulate 智优 submitting content for manual review")
    test_cat = st.selectbox("Category", MANUAL_REVIEW_CATEGORIES,
                            format_func=lambda x: f"{x}: {CATEGORY_NAMES.get(x, '')}")
    test_title = st.text_input("Title", value="Test Article Title")
    test_content = st.text_area("Content", value="This is test content for manual review...", height=150)

    # Find POC for this category
    test_poc = ""
    for poc, cats in POC_CATEGORIES.items():
        if test_cat in cats:
            test_poc = poc
            break

    st.caption(f"Will be assigned to: **{test_poc}**")
    if st.button("Submit for Review"):
        cid = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        submit_for_review(cid, test_cat, test_title, test_content, test_poc)
        st.success(f"✅ Submitted to {test_poc}'s review queue")
        st.rerun()
