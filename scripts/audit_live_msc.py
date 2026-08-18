import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://www.msccruises.de/de-de/Kreuzfahrtschiffe/MSC-Meraviglia.aspx',
    'https://www.msccruises.de/de-de/unsere-kreuzfahrtschiffe/msc-meraviglia.aspx',
    'https://www.msccruises.de/de-de/unsere-kreuzfahrtschiffe/msc-meraviglia/deckplan.aspx',
    'https://www.msccruises.com/en-gl/Discover-MSC/Cruise-Ships/MSC-Meraviglia.aspx',
    'https://www.msccruises.de/sitemap.xml',
    'https://www.msccruises.com/sitemap.xml',
    'https://mscpressarea.com',
    'https://www.mscbook.com'
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

for u in urls:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            content = resp.read()
            print(f'[OK] {u} -> Status: {resp.getcode()}, Size: {len(content)}')
            text = content.decode('utf-8', errors='ignore')
            pdf_links = re.findall(r'href=[\'"]([^\'"]+\.pdf[^\'"]*)[\'"]', text, re.IGNORECASE)
            print(f'     Found {len(pdf_links)} PDF links: {pdf_links[:5]}')
            deck_links = re.findall(r'href=[\'"]([^\'"]*deck[^\'"]*)[\'"]', text, re.IGNORECASE)
            print(f'     Found {len(deck_links)} deck links: {deck_links[:5]}')
    except Exception as e:
        print(f'[FAIL] {u} -> Error: {e}')
