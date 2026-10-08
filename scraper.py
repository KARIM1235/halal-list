import json, time, re, requests
from playwright.sync_api import sync_playwright

def get_pif(page):
    try:
        print("Going to PIF...")
        page.goto("https://pif.finance/crypto-halal-reports", timeout=90000, wait_until="domcontentloaded")
        page.wait_for_timeout(15000)
        html = page.content()
        print(f"PIF len {len(html)}")
        # حاول 2 طرق باش نلقاو Comfortable
        coins = set(re.findall(r'"symbol"\s*:\s*"([A-Z0-9]+)".{0,200}?"comfort"\s*:\s*"Comfortable"', html))
        if not coins:
            text = page.inner_text("body")
            print(f"PIF body preview: {text[:500]}")
            coins = set(re.findall(r'([A-Z]{2,7})\s*[-–]\s*Comfortable', text))
        print(f"PIF LIVE Comfortable: {len(coins)} {coins}")
        return coins
    except Exception as e:
        print(f"PIF error {e}")
        return set()

def get_ch(page):
    try:
        print("Going to CH...")
        page.goto("https://cryptohalal.cc/ar", timeout=90000, wait_until="domcontentloaded")
        page.wait_for_timeout(12000)
        html = page.content()
        print(f"CH len {len(html)}")
        coins = set(re.findall(r'<td[^>]*>\s*([A-Z0-9]{2,10})\s*</td>\s*<td[^>]*>\s*مباح', html))
        if not coins:
            coins = set(re.findall(r'<td[^>]*>\s*([A-Z0-9]{2,10})\s*</td>\s*<td[^>]*>\s*Halal', html, re.I))
        print(f"CH LIVE مباح: {len(coins)} {coins}")
        return coins
    except Exception as e:
        print(f"CH error {e}")
        return set()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled","--no-sandbox"])
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    # إخفاء أننا روبوت
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    pif = get_pif(page)
    ch = get_ch(page)
    browser.close()

merged = sorted(list(pif.union(ch)))
print(f"TOTAL from YOUR sites: {len(merged)}")

# إلا Cloudflare بقا بلوكا حتى stealth، نجيبو من Proxy مجاني كيجيب نفس المواقع LIVE
if len(merged) == 0:
    print("Playwright blocked by Cloudflare Turnstile, trying CORS proxy LIVE...")
    try:
        # هاد البروكسي كيجيب نفس صفحة PIF LIVE ولكن ما كيبلوكيش
        for proxy_url in [
            "https://api.allorigins.win/raw?url=https://pif.finance/crypto-halal-reports",
            "https://api.codetabs.com/v1/proxy?quest=https://pif.finance/crypto-halal-reports",
            "https://corsproxy.io/?https://pif.finance/crypto-halal-reports"
        ]:
            try:
                r = requests.get(proxy_url, timeout=20, headers={"User-Agent":"Mozilla/5.0"})
                print(f"Proxy {proxy_url[:30]} len {len(r.text)}")
                if len(r.text) > 2000:
                    coins = set(re.findall(r'"symbol"\s*:\s*"([A-Z0-9]+)".{0,200}?"comfort"\s*:\s*"Comfortable"', r.text))
                    if coins:
                        print(f"Proxy LIVE found {len(coins)} {coins}")
                        merged = sorted(list(coins))
                        pif = coins
                        break
            except Exception as e:
                print(f"Proxy fail {e}")

    except Exception as e:
        print(f"All proxy fail {e}")

if len(merged) == 0:
    raise Exception(f"PIF {len(pif)} CH {len(ch)} - Cloudflare قوي بزاف، خاص Worker خارجي")

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

print(f"✅ SAVED {len(merged)} LIVE from YOUR sites")
