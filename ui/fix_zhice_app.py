from pathlib import Path

p = Path(r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\ui\app_zhice.py')
content = p.read_text(encoding='utf-8')

# Fix: the placeholder insertion added literal \n
# Replace the broken line
content = content.replace('\\nwith tab_simulate:', '\nwith tab_simulate:')
content = content.replace('\\n\\nPLACEHOLDER_DASHBOARD\\n\\n', '')

p.write_text(content, encoding='utf-8')
print("Fixed escape chars")

# Verify
import ast
try:
    ast.parse(p.read_text(encoding='utf-8'))
    print("Syntax OK")
except SyntaxError as e:
    print(f"Syntax error: {e}")
