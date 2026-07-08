"""Fix all float conversion errors in app.py where percentage strings cause crashes."""
from pathlib import Path
import re

p = Path(r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\ui\app.py')
content = p.read_text(encoding='utf-8')

# Pattern 1: [float(row[c]) * 100 if pd.notna(row[c]) else 0 for c in _month_cols]
# Replace with safe version
old1 = 'pct_vals = [float(row.iloc[0][c]) * 100 if pd.notna(row.iloc[0][c]) else 0 for c in _month_cols]'
new1 = '''pct_vals = []
                        for c in _month_cols:
                            v = row.iloc[0][c]
                            if isinstance(v, str) and '%' in v:
                                try: pct_vals.append(float(v.replace('%','').replace('+','')))
                                except: pct_vals.append(0)
                            elif pd.notna(v):
                                try: pct_vals.append(float(v) * 100)
                                except: pct_vals.append(0)
                            else: pct_vals.append(0)'''

# Find all instances of the problematic pattern
# General pattern: float(something) where something could be a % string
count = 0

# Fix: _yoy_vals lines
lines = content.split('\n')
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Pattern: yoy_vals = [float(...) for c in ...]
    if 'float(row' in line and '_month_cols' in line and ('* 100' in line or 'for c in' in line):
        # Check if it's a list comprehension that needs fixing
        if '% ' not in line and "replace('%'" not in line:
            # This line needs fixing - replace float(row[c]) patterns
            # Replace inline float conversions with safe version
            line = re.sub(
                r'float\(row\[c\]\) \* 100 if pd\.notna\(row\[c\]\) else 0',
                r"(float(str(row[c]).replace('%','').replace('+','')) if isinstance(row[c], str) and '%' in str(row[c]) else (float(row[c]) * 100 if pd.notna(row[c]) else 0))",
                line
            )
            line = re.sub(
                r'float\(row\.iloc\[0\]\[c\]\) \* 100 if pd\.notna\(row\.iloc\[0\]\[c\]\) else 0',
                r"(float(str(row.iloc[0][c]).replace('%','').replace('+','')) if isinstance(row.iloc[0][c], str) and '%' in str(row.iloc[0][c]) else (float(row.iloc[0][c]) * 100 if pd.notna(row.iloc[0][c]) else 0))",
                line
            )
            count += 1
    
    # Pattern: float(row[col]) in lambda for YoY formatting
    if 'float(row[col])' in line and "replace('%'" not in line:
        if 'f"{float(row[col]):+.0%}"' in line or 'f"{float(row[col]):' in line:
            # Already fixed or different pattern, skip
            pass
    
    new_lines.append(line)
    i += 1

content = '\n'.join(new_lines)

# Also fix any remaining: [float(x) * 100 ... for c in _month_cols]
# Look for patterns like: vals = [float(row[c]) * 100 if pd.notna(row[c]) else 0 for c in
remaining = content.count('float(row[c]) * 100 if pd.notna(row[c]) else 0')
if remaining > 0:
    content = content.replace(
        'float(row[c]) * 100 if pd.notna(row[c]) else 0',
        '(float(str(row[c]).replace("%","").replace("+","")) if isinstance(row[c], str) and "%" in str(row[c]) else (float(row[c]) * 100 if pd.notna(row[c]) else 0))'
    )
    count += remaining

# Fix: float(row.iloc[0].get(c, 0)) patterns  
remaining2 = content.count('float(row.iloc[0].get(c, 0))')
# These are generally safe if they come from numeric data, leave them

p.write_text(content, encoding='utf-8')
print(f"Fixed {count + remaining} float conversion patterns")

# Verify
import ast
try:
    ast.parse(p.read_text(encoding='utf-8'))
    print("Syntax OK")
except SyntaxError as e:
    print(f"Syntax error: {e}")
