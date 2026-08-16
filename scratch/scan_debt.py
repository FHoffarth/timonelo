import os
import glob
import re

src_dir = r'C:\Users\Flo\Desktop\energyradar\timonelo\frontend\src'
all_files = glob.glob(os.path.join(src_dir, '**', '*.ts*'), recursive=True)

patterns = [
    r'TODO', r'FIXME', r'TBD', r'Coming Soon', r'Placeholder',
    r'Lorem', r'0 km', r'Deck\s*[\'\"`]\s*\+', r'\bN/A\b', r'\bUNKNOWN\b'
]

findings = []
for f in all_files:
    rel = os.path.relpath(f, src_dir)
    # ignore generated large db
    if 'generated' in rel:
        continue
    with open(f, 'r', encoding='utf-8', errors='ignore') as fh:
        for i, line in enumerate(fh, 1):
            for pat in patterns:
                if re.search(pat, line, re.IGNORECASE):
                    findings.append((rel, i, pat, line.strip()))

print(f'Total findings: {len(findings)}')
for fpath, line_no, pat, text in findings:
    print(f'{fpath}:{line_no} [{pat}] -> {text[:100]}')
