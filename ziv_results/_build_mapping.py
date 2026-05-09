import csv, re, subprocess
from pathlib import Path
from collections import defaultdict

root = Path(r'c:\Users\Cyrus-MSI\Desktop\ziv_bike_matcher - 複製\ziv_results')
missing_path = root / 'missing_thumbs.csv'
photo_path = root / 'photo_index.csv'
map_out = root / 'missing_filename_mapping.csv'
new_photo_out = root / 'photo_index_remapped.csv'

ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
img_pat = re.compile(r"<img[^>]+src=['\"]([^'\"]+)['\"]", re.I)
name_pat = re.compile(r"s_\d+\.(?:jpg|jpeg|png)$", re.I)

def fetch(url):
    p = subprocess.run(['curl.exe','-L','--max-time','80','-A',ua,'-e','https://www.ziv.com.tw/',url], capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return p.stdout or ''

missing_rows = list(csv.DictReader(missing_path.open('r', encoding='utf-8-sig', newline='')))
by_page = defaultdict(list)
for r in missing_rows:
    by_page[r['page_url']].append(r)

page_new_names = {}
for page in sorted(by_page.keys()):
    html = fetch(page)
    names = []
    seen = set()
    for src in img_pat.findall(html):
        m = name_pat.search(src)
        if not m:
            continue
        n = m.group(0)
        if n in seen:
            continue
        seen.add(n)
        names.append(n)
    page_new_names[page] = names

mappings = []
for page, olds in by_page.items():
    news = page_new_names.get(page, [])
    for i, old in enumerate(olds):
        new_name = news[i] if i < len(news) else ''
        status = 'mapped' if new_name else 'unmapped'
        mappings.append({
            'page_url': page,
            'old_filename': old['filename'],
            'new_filename': new_name,
            'status': status
        })

with map_out.open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['page_url','old_filename','new_filename','status'])
    w.writeheader()
    w.writerows(mappings)

old2new = {m['old_filename']: m['new_filename'] for m in mappings if m['status']=='mapped'}
photo_rows = list(csv.DictReader(photo_path.open('r', encoding='utf-8-sig', newline='')))
for r in photo_rows:
    old = r['filename']
    if old in old2new:
        new = old2new[old]
        r['filename'] = new
        r['img_url'] = re.sub(r"s_\d+\.(?:jpg|jpeg|png)$", new, r['img_url'], flags=re.I)

with new_photo_out.open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=photo_rows[0].keys())
    w.writeheader()
    w.writerows(photo_rows)

mapped = sum(1 for m in mappings if m['status']=='mapped')
unmapped = len(mappings) - mapped
print(f'pages={len(by_page)}')
print(f'missing_rows={len(mappings)}')
print(f'mapped={mapped}')
print(f'unmapped={unmapped}')
print(f'mapping_file={map_out}')
print(f'remapped_csv={new_photo_out}')
