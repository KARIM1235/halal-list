import os, json, time, re
from playwright.sync_api import sync_playwright

PIF_EMAIL=os.getenv("ciciy17061@rastern.com") or ""
PIF_PASS=os.getenv("Ciciy17061@") or ""

def get_pif(page):
    if not PIF_EMAIL or not PIF_PASS:
        print("PIF_EMAIL/PASSWORD not set in Secrets - skipping PIF")
        return set()
    print(f"=== PIF LOGIN {PIF_EMAIL} ===")
    page.goto("https://pif.finance/auth/signin?callbackUrl=%2Flogin", timeout=90000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    try:
        if page.locator('input[type="email"]').count()>0:
            page.locator('input[type="email"]').first.fill(PIF_EMAIL)
            page.wait_for_timeout(500)
            page.locator('input[type="password"]').first.fill(PIF_PASS)
            page.wait_for_timeout(500)
            page.locator('button[type="submit"]').first.click()
            page.wait_for_timeout(10000)
            print(f"After login URL {page.url}")
    except Exception as e:
        print(f"PIF fill err {e}")
    
    page.goto("https://pif.finance/crypto-halal-reports", timeout=90000, wait_until="domcontentloaded")
    page.wait_for_timeout(10000)
    html=page.content()
    if "Welcome back" in html:
        print("PIF still login page - check if account needs email/pass not Google only")
        return set()
    coins=set(re.findall(r'"symbol"\s*:\s*"([A-Z0-9]+)".{0,300}?"comfort"\s*:\s*"Comfortable"', html, re.I))
    print(f"PIF LIVE {len(coins)} {coins}")
    return coins

def get_ch(page):
    page.goto("https://cryptohalal.cc/ar", timeout=90000, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)
    coins=set()
    try:
        rows=page.locator("table tr").all()
        for row in rows:
            txt=row.inner_text()
            if "مباح" in txt:
                m=re.search(r'\b([A-Z]{2,10})\b', txt)
                if m and m.group(1) not in ["USDT","USDC"]: coins.add(m.group(1).upper())
    except: pass
    print(f"CH LIVE مباح: {len(coins)} {coins}")
    return coins

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled","--no-sandbox"])
    page=browser.new_page()
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    pif=get_pif(page)
    ch=get_ch(page)
    browser.close()

merged=sorted(list(pif.union(ch)))
if not merged: merged=sorted(list(ch))
print(f"FINAL LIVE {len(merged)} PIF={len(pif)} CH={len(ch)}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({"updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"), "live": True, "sources": ["PIF","CH"], "counts": {"pif": len(pif), "ch": len(ch)}, "count": len(merged), "coins": merged, "pairs": [f"{c}/USDT" for c in merged]}, f, indent=2, ensure_ascii=False)
