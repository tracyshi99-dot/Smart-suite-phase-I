"""
Smart Suite Automation Cron Job
================================
独立脚本，定时检查所有用户的自动化规则并执行。
可配合 Windows Task Scheduler 定时运行。

用法：
  python automation_cron.py              # 执行一次
  python automation_cron.py --loop 300   # 每 300 秒循环执行

Windows Task Scheduler 设置：
  程序: python
  参数: automation_cron.py
  触发: 每 1 小时 / 每天固定时间
"""
import sys
import os
import json
import time
import math
import logging
from pathlib import Path
from datetime import datetime

# Setup paths
BASE_PATH = Path(__file__).parent
sys.path.insert(0, str(BASE_PATH / "ui"))
os.chdir(str(BASE_PATH / "ui"))

OUTPUT_PATH = BASE_PATH / "output"
INPUT_PATH = BASE_PATH / "input"

# Setup logging
LOG_FILE = BASE_PATH / "logs" / "automation.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger("automation")


def load_csv_safe(path):
    """Load CSV safely."""
    import pandas as pd
    try:
        return pd.read_csv(path, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
    except Exception:
        try:
            return pd.read_csv(path, encoding="utf-8", on_bad_lines="skip", engine="python")
        except Exception:
            return pd.DataFrame()


def load_users():
    """Load user list."""
    users_file = OUTPUT_PATH / "users.json"
    if users_file.exists():
        data = json.loads(users_file.read_text(encoding="utf-8"))
        return data.get("allowed", [])
    return []


def load_rules(user: str) -> list:
    """Load automation rules for a user."""
    rules_file = OUTPUT_PATH / "requests" / user / "automation_rules.json"
    if rules_file.exists():
        try:
            return json.loads(rules_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def load_exec_log(user: str) -> dict:
    """Load execution log."""
    log_file = OUTPUT_PATH / "requests" / user / "automation_log.json"
    if log_file.exists():
        try:
            return json.loads(log_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_exec_log(user: str, exec_log: dict):
    """Save execution log."""
    log_file = OUTPUT_PATH / "requests" / user / "automation_log.json"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text(json.dumps(exec_log, ensure_ascii=False, indent=2), encoding="utf-8")


def get_user_batch(user: str) -> str:
    """Get the batch ID for a user."""
    return f"batch_{user}"


def check_condition(rule_name: str, batch_id: str) -> bool:
    """Check if a rule's trigger condition is satisfied."""
    import pandas as pd

    zhiku_file = OUTPUT_PATH / batch_id / "01_zhiku" / "zhiku_ai_queries.csv"
    zhizao_file = OUTPUT_PATH / batch_id / "02_zhizao" / "zhizao_draft_content.csv"
    zhiyou_file = OUTPUT_PATH / batch_id / "03_zhiyou" / "zhiyou_optimized_content.csv"
    zhibu_dir = OUTPUT_PATH / batch_id / "04_zhibu"

    if "智库 → 智造" in rule_name or "智测 → 智造" in rule_name or "Research → Creation" in rule_name:
        if zhiku_file.exists():
            df = load_csv_safe(zhiku_file)
            if not df.empty and len(df) >= 5:
                if "is_selected" in df.columns:
                    selected = df["is_selected"].astype(str).str.strip().str.upper().isin(["TRUE", "1", "YES"])
                    return selected.sum() >= 5
                return len(df) >= 5
        return False

    elif "智造 → 智优" in rule_name or "Creation → Optimization" in rule_name:
        if zhizao_file.exists():
            df = load_csv_safe(zhizao_file)
            return not df.empty and len(df) >= 1
        return False

    elif "智优 → 智布" in rule_name or "Optimization → Publishing" in rule_name:
        if zhiyou_file.exists():
            df = load_csv_safe(zhiyou_file)
            if not df.empty and "overall_score" in df.columns:
                scores = pd.to_numeric(df["overall_score"], errors="coerce").fillna(0)
                return len(scores) > 0 and scores.min() >= 4.0
        return False

    elif "智布 → 发布" in rule_name or "Publishing → Distribute" in rule_name:
        if zhibu_dir.exists():
            return any(zhibu_dir.glob("*.json"))
        return False

    return False


def execute_action(rule_name: str, batch_id: str) -> tuple:
    """Execute a rule action. Returns (success, message)."""
    try:
        from engine import run_zhizao, run_zhiyou_score, run_zhiyou_execute, run_zhibu

        if "智库 → 智造" in rule_name or "智测 → 智造" in rule_name or "Research → Creation" in rule_name:
            result = run_zhizao(batch_id, content_limit=5)
            if result.get("success"):
                return True, f"Generated {result.get('articles_count', 0)} articles"
            return False, result.get("error", "Unknown error")

        elif "智造 → 智优" in rule_name or "Creation → Optimization" in rule_name:
            result = run_zhiyou_score(batch_id)
            if result.get("success"):
                run_zhiyou_execute(batch_id)
                return True, f"Scored & optimized {result.get('scored_count', 0)} articles"
            return False, result.get("error", "Unknown error")

        elif "智优 → 智布" in rule_name or "Optimization → Publishing" in rule_name:
            result = run_zhibu(batch_id)
            if result.get("success"):
                return True, f"Published {result.get('items_count', 0)} items"
            return False, result.get("error", "Unknown error")

        elif "智布 → 发布" in rule_name or "Publishing → Distribute" in rule_name:
            return True, "Distribution step — manual review recommended"

        return False, "Unknown rule"
    except ImportError as e:
        return False, f"Import error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def run_all_users():
    """Run automation check for all users.
    Each user's own rules (set in 智中枢) are checked and executed independently.
    Admin only needs to run this script — users don't need to do anything."""
    users = load_users()
    today = datetime.now().strftime("%Y-%m-%d")
    total_executed = 0

    log.info(f"=== Automation check started ({len(users)} users) ===")

    for user in users:
        batch_id = get_user_batch(user)
        # Skip users without a batch directory
        batch_dir = OUTPUT_PATH / batch_id
        if not batch_dir.exists():
            continue

        rules = load_rules(user)
        if not rules:
            continue

        enabled_rules = [r for r in rules if r.get("enabled", False)]
        if not enabled_rules:
            continue

        exec_log = load_exec_log(user)
        log_changed = False

        for rule in enabled_rules:
            rule_name = rule.get("name", "")

            # Skip if already executed today
            last_exec = exec_log.get(rule_name, {}).get("last_date", "")
            if last_exec == today:
                continue

            # Check condition
            if check_condition(rule_name, batch_id):
                log.info(f"  [{user}] Rule triggered: {rule_name}")
                success, msg = execute_action(rule_name, batch_id)

                status = "success" if success else "failed"
                log.info(f"  [{user}] Result: {status} — {msg}")

                exec_log[rule_name] = {
                    "last_date": today,
                    "last_result": status,
                    "message": msg,
                    "time": datetime.now().strftime("%H:%M:%S"),
                }
                log_changed = True
                total_executed += 1

        if log_changed:
            save_exec_log(user, exec_log)

    log.info(f"=== Automation check complete. {total_executed} rules executed. ===")
    return total_executed


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Smart Suite Automation Cron")
    parser.add_argument("--loop", type=int, default=0,
                        help="Loop interval in seconds (0 = run once)")
    args = parser.parse_args()

    if args.loop > 0:
        log.info(f"Starting automation loop (interval: {args.loop}s)")
        while True:
            try:
                run_all_users()
            except Exception as e:
                log.error(f"Error in automation loop: {e}")
            time.sleep(args.loop)
    else:
        run_all_users()


if __name__ == "__main__":
    main()
