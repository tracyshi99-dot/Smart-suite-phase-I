from pathlib import Path

p = Path(r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\ui\app.py')
content = p.read_text(encoding='utf-8')

# Fix: share_yoy calculation to use bps
content = content.replace(
    'share_yoy = share_a - share_p',
    'share_yoy = (share_a/100 - share_p/100) * 10000'
)

# Fix: format as bps instead of ppts
content = content.replace(
    'f"{share_yoy:+.1f}ppts"',
    'f"{share_yoy:+,.0f} bps"'
)

# Also fix the Type label
content = content.replace(
    '"Type": ["Actual", "PY", "YoY \u0394"]',
    '"Type": ["Actual", "PY", "YoY (bps)"]'
)

p.write_text(content, encoding='utf-8')
print("Done - changed to bps")
