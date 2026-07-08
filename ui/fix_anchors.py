from pathlib import Path

p = Path(r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\ui\gen_wiki.py')
content = p.read_text(encoding='utf-8')

# Replace div wrappers with <a> links in the workflow EN section
# Pattern: <div style="background:#0f1117;border:1px solid #COLOR;..."><div style="font-size:11px;color:#COLOR;font-weight:600;">NAME</div></div>
# Replace with: <a href="#ID" style="text-decoration:none;background:#0f1117;border:1px solid #COLOR;..."><div style="font-size:11px;color:#COLOR;font-weight:600;">NAME</div></a>

replacements = [
    ('Intelligencer', '#ffa726', 'zhiku'),
    ('Creator', '#ffcc02', 'zhizao'),
    ('Optimizer', '#e91e63', 'zhiyou'),
    ('Publisher', '#29b6f6', 'zhibu'),
    ('Distributor', '#26c6da', 'zhichuan'),
    ('Analyzer', '#ab47bc', 'zhixi'),
    ('Orchestrator', '#ff6b35', 'zhishu'),
]

for name, color, tid in replacements:
    old = f'<div style="background:#0f1117;border:1px solid {color};border-radius:8px;padding:6px 10px;text-align:center;min-width:fit-content;"><div style="font-size:11px;color:{color};font-weight:600;">{name}</div></div>'
    new = f'<a href="#{tid}" style="text-decoration:none;background:#0f1117;border:1px solid {color};border-radius:8px;padding:6px 10px;text-align:center;min-width:fit-content;display:inline-block;"><div style="font-size:11px;color:{color};font-weight:600;">{name}</div></a>'
    if old in content:
        content = content.replace(old, new)
        print(f"  Linked: {name} -> #{tid}")
    else:
        print(f"  NOT FOUND: {name}")

p.write_text(content, encoding='utf-8')
print("Done")
