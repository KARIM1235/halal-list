import os, json, time, re
from playwright.sync_api import sync_playwright

PIF_EMAIL=os.getenv("ciciy17061@rastern.com")
PIF_PASS=os.getenv("Ciciy17061@")
CH_EMAIL=os.getenv("ciciy17061@rastern.com")
CH_PASS=os.getenv("Ciciy17061@")

def get_pif(page):
    print(f"Logging to PIF with {PIF_EMAIL}...")
    page.goto("https://pif.finance/login", timeout=90000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    # كيعمر الفورم أوتوماتيك
    try:
        page.fill('input[type="email"]', PIF_EMAIL)
        page.fill('input[type="password"]', PIF_PASS)
        page.click('button:has-text("Log in"), button:has-text("Continue"), button[type="submit"]')
        page.wait_for_timeout(8000)
        print(f"After login URL: {page.url}")
    except Exception as e:
        print(f"PIF login fill err {e} - trying Google form")
    
    page.goto("https://pif.finance/crypto-halal-reports", timeout=90000)
    page.wait_for_timeout(12000)
    html=page.content()
    print(f"PIF after login len {len(html)}")
    
    coins=set(re.findall(r'"symbol"\s*:\s*"([A-Z0-9]+)".{0,200}?"comfort"\s*:\s*"Comfortable"', html, re.I))
    if not coins:
        text=page.inner_text("body")
        print(f"PIF text preview {text[:800]}")
        coins=set(re.findall(r'([A-Z]{2,7})\s*[-–]\s*Comfortable', text))
        # حتى طريقة ديال الجدول
        if not coins:
            try:
                rows=page.locator("tr").all()
                for r in rows:
                    t=r.inner_text()
                    if "Comfortable" in t:
                        m=re.search(r'\b([A-Z]{2,6})\b', t)
                        if m: coins.add(m.group(1))
            except: pass
    print(f"PIF LIVE Comfortable: {len(coins)} {coins}")
    return coins

def get_ch(page):
    print("Going to CryptoHalal...")
    # إلا كيطلب login
    if CH_EMAIL:
        try:
            page.goto("https://cryptohalal.cc/login", timeout=60000)
            page.wait_for_timeout(2000)
            page.fill('input[type="email"], input[name="email"]', CH_EMAIL)
            page.fill('input[type="password"]', CH_PASS)
            page.click('button[type="submit"]')
            page.wait_for_timeout(5000)
        except Exception as e:
            print(f"CH login optional {e}")
    
    page.goto("https://cryptohalal.cc/ar", timeout=90000, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    html=page.content()
    print(f"CH len {len(html)}")
    
    coins=set()
    for pat in [r'<td[^>]*>\s*([A-Z0-9]{2,10})\s*</td>\s*<td[^>]*>\s*مباح', r'([A-Z]{2,10})\s*</td>\s*<td[^>]*>مباح']:
        coins.update(re.findall(pat, html, re.I))
    
    if not coins:
        try:
            rows=page.locator("table tr").all()
            print(f"CH rows {len(rows)}")
            for row in rows:
                txt=row.inner_text()
                if "مباح" in txt:
                    m=re.search(r'\b([A-Z]{2,10})\b', txt)
                    if m and len(m.group(1))>=2:
                        coins.add(m.group(1).upper())
        except Exception as e:
            print(f"CH locator err {e}")
    
    print(f"CH LIVE مباح: {len(coins)} {coins}")
    return coins

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled","--no-sandbox"])
    page=browser.new_page(user_agent="Mozilla/5.0 Windows NT 10.0 Win64 x64 Chrome/122.0")
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    pif=get_pif(page)
    ch=get_ch(page)
    browser.close()

merged=sorted(list(pif.union(ch)))
print(f"FINAL TOTAL LIVE from YOUR accounts: {len(merged)} PIF={len(pif)} CH={len(ch)} {merged}")

if len(merged)==0:
    raise Exception(f"Login failed? PIF len {len(pif)} CH len {len(ch)} - check secrets")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
        "live": True,
        "sources": ["LIVE https://pif.finance/crypto-halal-reports Comfortable ONLY (logged in)","LIVE https://cryptohalal.cc/ar مباح ONLY"],
        "counts": {"pif_comfortable": len(pif), "cryptohalal_mubah": len(ch)},
        "count": len(merged),
        "coins": merged,
        "pairs": [f"{c}/USDT" for c in merged]
    }, f, indent=2, ensure_ascii=False)
