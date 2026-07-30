import sys, re
path = r'c:\Users\Personal\OneDrive\Desktop\Auto-Apply-AI\frontend\src\app\page.tsx'
with open(path, 'r', encoding='utf-8') as f: content = f.read()
content = content.replace('"Bearer dev-mock-${username}"', '`Bearer dev-mock-${username}`')
with open(path, 'w', encoding='utf-8') as f: f.write(content)
print('Fixed!')
