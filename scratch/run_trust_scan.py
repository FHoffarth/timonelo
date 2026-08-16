import os
import glob
import re

root = r'C:\Users\Flo\Desktop\energyradar\timonelo'
files = glob.glob(os.path.join(root, 'frontend', 'src', '**', '*.ts*'), recursive=True)
files.append(os.path.join(root, 'README.md'))

queries = ['verified', 'digital twin', 'guarantee', '100%']

with open(r'C:\Users\Flo\Desktop\energyradar\timonelo\scratch\trust_scan.txt', 'w', encoding='utf-8') as out:
    for f in files:
        if 'generated' in f:
            continue
        rel = os.path.relpath(f, root)
        with open(f, 'r', encoding='utf-8', errors='ignore') as fh:
            for i, line in enumerate(fh, 1):
                for q in queries:
                    if re.search(r'\b' + re.escape(q) + r'\b', line, re.IGNORECASE):
                        out.write(f'{rel}:{i} [{q}] -> {line.strip()}\n')

print('Trust scan complete.')
