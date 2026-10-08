import json, time, re
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

def get_pif(page):
    page.goto("https://pif.finance/crypto-halal-reports", timeout=90000)
    page.wait_for_timeout(15000) # نخليو Cloudflare يدوز
    html = page.content()
    print(f"PIF len {len(html)}")
    coins = set(re.findall(r'"symbol"\s*:\s*"([A-Z0-9]+)".{0,200}?"comfort"\s*:\s*"Comfortable"', html))
    if not coins:
        text = page.inner_text("body")[:20000]
        coins = set(re.findall(r'([A-Z]{2,7})\s*[-–]\s*Comfortable', text))
    print(f"PIF LIVE Comfortable: {len(coins)} {coins}")
    return coins

def get_ch(page):
    page.goto("https://cryptohalal.cc/ar", timeout=90000)
    page.wait_for_timeout(12000)
    html = page.content()
    print(f"CH len {len(html)}")
    coins = set(re.findall(r'<td[^>]*>\s*([A-Z0-9]{2,10})\s*</td>\s*<td[^>]*>\s*مباح', html))
    if not coins:
        coins = set(re.findall(r'<td[^>]*>\s*([A-Z0-9]{2,10})\s*</td>\s*<td[^>]*>\s*Halal', html, re.I))
    print(f"CH LIVE مباح: {len(coins)} {coins}")
    return coins

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
    page = browser.new_page()
    stealth_sync(page)
    
    pif = get_pif(page)
    ch = get_ch(page)
    
    browser.close()

merged = sorted(list(pif.union(ch)))
print(f"TOTAL LIVE من مصادرك فقط: {len(merged)}")

if len(merged)==0:
    # باش يبقى خضر حتى إلا تبلوكا، نكتبو ملف فيه السبب ولكن ما نطيحوش الـ build
    # ولكن نتا بغيتي غير LIVE، فكنخليو يطيح باش نعرفو
    raise Exception(f"PIF {len(pif)} CH {len(ch)} - Cloudflare Turnstile مازال بلوكا حتى stealth")

out={
 "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
 "live": True,
 "sources": ["LIVE https://pif.finance/crypto-halal-reports Comfortable ONLY","LIVE https://cryptohalal.cc/ar مباح ONLY"],
 "counts": {"pif_comfortable": len(pif), "cryptohalal_mubah": len(ch)},
 "count": len(merged),
 "coins": merged,
 "pairs": [f"{c}/USDT" for c in merged]
}
with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump(out,f,indent=2,ensure_ascii=False)
