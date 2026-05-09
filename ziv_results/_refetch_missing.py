import csv, re, subprocess
from pathlib import Path

root = Path(r'c:\Users\Cyrus-MSI\Desktop\ziv_bike_matcher - 複製\ziv_results')
thumb = root / 'thumbs'
missing_csv = root / 'missing_thumbs.csv'
ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'

rows = list(csv.DictReader(missing_csv.open('r', encoding='utf-8-sig', newline='')))
page_urls = sorted(set(r['page_url'] for r in rows if r.get('page_url')))

img_urls = set()
img_pat = re.compile(r"<img[^>]+src=['\"]([^'\"]+)['\"]", re.I)
file_pat = re.compile(r"/tmp/.+?/s_\d+\.(jpg|jpeg|png)$", re.I)

def curl_text(url):
    p = subprocess.run([
        'curl.exe','-L','--max-time','60','-A',ua,'-e','https://www.ziv.com.tw/',url
    ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return p.stdout if p.stdout else ''

def curl_file(url, outpath):
    p = subprocess.run([
        'curl.exe','-L','--max-time','40','-A',ua,'-e','https://www.ziv.com.tw/',url,'-o',str(outpath)
    ], capture_output=True, text=True)
    return p.returncode == 0 and outpath.exists() and outpath.stat().st_size > 0

for u in page_urls:
    html = curl_text(u)
    if not html:
        continue
    for src in img_pat.findall(html):
        if src.startswith('./'):
            src = 'https://www.ziv.com.tw/' + src[2:]
        elif src.startswith('/'):
            src = 'https://www.ziv.com.tw' + src
        elif not src.startswith('http'):
            src = 'https://www.ziv.com.tw/' + src
        if file_pat.search(src):
            img_urls.add(src)

thumb.mkdir(parents=True, exist_ok=True)
downloaded = skipped = failed = 0
for img in sorted(img_urls):
    name = img.rsplit('/', 1)[-1]
    out = thumb / name
    if out.exists():
        skipped += 1
        continue
    ok = curl_file(img, out)
    if ok:
        downloaded += 1
    else:
        failed += 1
        try:
            if out.exists():
                out.unlink()
        except Exception:
            pass

print(f'pages={len(page_urls)}')
print(f'img_urls_found={len(img_urls)}')
print(f'downloaded={downloaded}')
print(f'skipped_existing={skipped}')
print(f'failed={failed}')
