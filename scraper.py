import json, time, re
from playwright.sync_api import sync_playwright

def get_pif(page):
    page.goto("https://pif.finance/crypto-halal-reports", wait_until="networkidle", timeout=60000)
    time.sleep(5)
    html = page.content()
    # كنجبدو Comfortable فقط
    coins = set(re.findall(r'"symbol"\s*:\s*"([A-Z0-9]+)".{0,150}?"comfort"\s*:\s*"Comfortable"', html))
    if not coins:
        coins = set(re.findall(r'([A-Z]{2,7})\s*-\s*Comfortable', html))
    print(f"PIF LIVE Comfortable: {len(coins)} {coins}")
    return coins

def get_ch(page):
    page.goto("https://cryptohalal.cc/ar", wait_until="networkidle", timeout=60000)
    time.sleep(5)
    html = page.content()
    coins = set(re.findall(r'<td[^>]*>\s*([A-Z0-9]{2,10})\s*</td>\s*<td[^>]*>\s*مباح', html))
    if not coins:
        page.goto("https://cryptohalal.cc/", wait_until="networkidle", timeout=60000)
        html = page.content()
        coins = set(re.findall(r'<td[^>]*>\s*([A-Z0-9]{2,10})\s*</td>\s*<td[^>]*>\s*Halal', html, re.I))
    print(f"CryptoHalal LIVE مباح: {len(coins)} {coins}")
    return coins

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(user_agent="Mozilla/5.0 Windows NT 10.0 Win64 x64 AppleWebKit/537.36")
    
    pif = get_pif(page)
    ch = get_ch(page)
    
    browser.close()

merged = sorted(list(pif.union(ch)))
print(f"TOTAL LIVE من مصادرك فقط: {len(merged)}")

if len(merged) == 0:
    raise Exception("PIF و Cryptohalal مازال بلوكاو حتى المتصفح - خاص نزيدو الانتظار")

out = {
    "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
    "live": True,
    "sources": ["LIVE https://pif.finance/crypto-halal-reports Comfortable ONLY", "LIVE https://cryptohalal.cc/ar مباح ONLY"],
    "counts": {"pif_comfortable": len(pif), "cryptohalal_mubah": len(ch)},
    "count": len(merged),
    "coins": merged,
    "pairs": [f"{c}/USDT" for c in merged]
}

with open("halal_pairs.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(f"✅ SAVED LIVE {len(merged)} from YOUR sites only")
