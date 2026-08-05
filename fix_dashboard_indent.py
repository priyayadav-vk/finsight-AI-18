import re
p = r"C:\Users\dell\OneDrive\Desktop\finsightai\pages\dashboard.py"
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()
# Replace occurrences of a literal 'n' at beginning of lines that were inserted accidentally
s2 = re.sub(r"\r?\n\s*n\s+", "\n        ", s)
if s2 != s:
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s2)
    print('fixed')
else:
    print('no-change')
