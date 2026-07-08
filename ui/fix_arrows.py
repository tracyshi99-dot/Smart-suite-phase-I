from pathlib import Path

p = Path(r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\ui\gen_wiki.py')
content = p.read_text(encoding='utf-8')

old = '<div style="color:#2a2f4a;font-size:14px;">&#8594;</div>'
new = '<div style="color:#8892b0;font-size:20px;font-weight:700;">&#10132;</div>'

count = content.count(old)
content = content.replace(old, new)
p.write_text(content, encoding='utf-8')
print(f"Replaced {count} arrows")
