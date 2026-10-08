import os, json, time, re
from playwright.sync_api import sync_playwright

PIF_EMAIL=os.getenv("ciciy17061@rastern.com")
PIF_PASS=os.getenv("Ciciy17061@")

def get_pif(page):
    print(f"=== PIF LOGIN TRY {PIF_EMAIL} ===")
    # 1 - سير لصفحة login
    page.goto("https://pif.finance/login", timeout=90000, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    print(f"Login page len {len(page.content())} url {page.url}")
    
    # جرب نلقاو inputs
    try:
        # إلا كاين Google button، نقلبو على Email link
        if page.locator('text="Continue with Email"').count()>0:
            page.click('text="Continue with Email"')
            page.wait_for_timeout(2000)
        
        email_input = page.locator('input[type="email"], input[name="email"], input[placeholder*="mail" i]').first
        pass_input = page.locator('input[type="password"]').first
        
        if email_input.count()>0:
            print("Filling email/pass...")
            email_input.fill(PIF_EMAIL)
            page.wait_for_timeout(500)
            pass_input.fill(PIF_PASS)
            page.wait_for_timeout(500)
            
            # كليكي على أول زر Submit
            page.locator('button[type="submit"], button:has-text("Log in"), button:has-text("Sign in"), button:has-text("Continue")').first.click()
            page.wait_for_timeout(10000)
            print(f"After submit URL: {page.url}")
            print(f"After submit title: {page.title()}")
        else:
            print("No email input found - site uses Google only?")
            print(page.inner_text("body")[:1000])
    except Exception as e:
        print(f"PIF fill err {e}")
        print(page.inner_text("body")[:1000])

    # 2 - دابا سير للـ reports
    page.goto("https://pif.finance/crypto-halal-reports", timeout=90000, wait_until="networkidle")
    page.wait_for_timeout(12000)
    html = page.content()
    print(f"PIF reports page len {len(html)} url {page.url}")
    
    if "Welcome back" in html or "Continue with Google" in html:
        print("STILL LOGIN PAGE - PIF login failed, needs Google OAuth")
        # جرب API مباشرة
        try:
            resp = page.request.get("https://pif.finance/api/crypto/reports", timeout=20000)
            print(f"PIF API status {resp.status} len {len(resp.text())}")
            if "Comfortable" in resp.text():
                html = resp.text()
        except Exception as e:
            print(f"PIF API err {e}")
        return set()
    
    coins=set(re.findall(r'"symbol"\s*:\s*"([A-Z0-9]+)".{0,300}?"comfort"\s*:\s*"Comfortable"', html, re.I))
    if not coins:
        # fallback text
        text = page.inner_text("body")
        coins=set(re.findall(r'\b([A-Z]{2,6})\b.*Comfortable', text))
    
    print(f"PIF LIVE Comfortable: {len(coins)} {coins}")
    return coins

def get_ch(page):
    page.goto("https://cryptohalal.cc/ar", timeout=90000, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    html=page.content()
    coins=set()
    # هادي هي اللي خدمات عندك
    try:
        rows=page.locator("table tr").all()
        for row in rows:
            txt=row.inner_text()
            if "مباح" in txt:
                m=re.search(r'\b([A-Z]{2,10})\b', txt)
                if m: coins.add(m.group(1).upper())
    except: pass
    if not coins:
        coins=set(re.findall(r'<td[^>]*>\s*([A-Z0-9]{2,10})\s*</td>\s*<td[^>]*>\s*مباح', html, re.I))
    # نحيدو USDT/USDC حيث ماشي عملات للتداول
    coins={c for c in coins if c not in ["USDT","USDC"]}
    print(f"CH LIVE مباح (بدون stablecoins): {len(coins)} {coins}")
    return coins

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled","--no-sandbox"])
    page=browser.new_page(user_agent="Mozilla/5.0 Windows NT 10.0 Win64 x64 Chrome/122.0")
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    pif=get_pif(page)
    ch=get_ch(page)
    browser.close()

merged=sorted(list(pif.union(ch)))
if len(merged)==0:
    merged=sorted(list(ch)) # على الأقل CH

print(f"FINAL LIVE: {len(merged)} PIF={len(pif)} CH={len(ch)}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
        "live": True,
        "sources": ["LIVE https://pif.finance/crypto-halal-reports Comfortable (login)","LIVE https://cryptohalal.cc/ar مباح"],
        "counts": {"pif_comfortable": len(pif), "cryptohalal_mubah": len(ch)},
        "count": len(merged),
        "coins": merged,
        "pairs": [f"{c}/USDT" for c in merged]
    }, f, indent=2, ensure_ascii=False)
