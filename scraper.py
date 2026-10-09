import re, json, time
from playwright.sync_api import sync_playwright
from datetime import datetime

all_pairs = set()

urls = [
    "https://announcements.bybit.com/en/article/islamic-account-expansion-continues-batch-2-brings-20-more-shariah-compliant-pairs-bltae5e0c1d2f/",
    "https://announcements.bybit.com/en/article/bybit-islamic-account-expands-20-new-shariah-compliant-trading-pairs-now-available-blt8c1b3f2a9/",
    "https://www.bybit.com/en/help-center/article/Islamic-Account-Introduction",
    "https://www.bybit.com/en/help-center/s/article/Islamic-Account-Supported-Pairs"
]

print("Fetching LIVE from Bybit Islamic with browser (bypass Cloudflare)...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(user_agent="Mozilla/5.0")

    for url in urls:
        try:
            print(f"\n-> Scanning {url[:80]}...")
            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(5)
            html = page.content()

            # قلب على كل الأزواج XXX/USDT
            found = re.findall(r'\b([A-Z0-9]{1,12}/USDT)\b', html)
            print(f" Found {len(found)} raw matches")

            for pair in found:
                if pair in ["BYBIT/USDT", "API/USDT", "HTML/USDT", "USDT/USDT"]:
                    continue
                # فلتر: خاص يكون الرمز فيه حرف
                base = pair.split("/")[0]
                if len(base) < 1 or len(base) > 12:
                    continue
                if pair not in all_pairs:
                    print(f" + MUBAH AUTO {pair}")
                all_pairs.add(pair)

        except Exception as e:
            print(f" Error {url}: {e}")

    browser.close()

# إلا ما لقيناش بزاف، جيب من الإعلانات مباشرة بالـ API ديال Bybit
if len(all_pairs) < 10:
    print("\nFallback: scraping announcement list page with browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://announcements.bybit.com/en/?search=islamic", wait_until="networkidle", timeout=60000)
            time.sleep(5)
            # كليكي على كل إعلان فيه islamic
            links = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a')).map(a=>a.href).filter(h=>h.toLowerCase().includes('islamic'))
            }""")
            for link in links[:5]:
                print(f"Found islamic article: {link}")
                page.goto(link, wait_until="networkidle", timeout=30000)
                time.sleep(3)
                html = page.content()
                found = re.findall(r'\b([A-Z0-9]{1,12}/USDT)\b', html)
                for pair in found:
                    if pair not in all_pairs and pair not in ["BYBIT/USDT"]:
                        print(f" + MUBAH AUTO {pair} from {link[:30]}")
                        all_pairs.add(pair)
        except Exception as e:
            print(f"Fallback error {e}")
        browser.close()

coins = sorted(list(set([p.split("/")[0] for p in all_pairs])))
pairs = sorted(list(all_pairs))

print("\n==============================")
print(f"TOTAL AUTO {len(pairs)} حلال LIVE من Bybit Islamic")
print(f"Pairs: {pairs[:20]}...")
print("==============================")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC LIVE BYBIT AUTO"),
        "live": True,
        "source": "AUTO Playwright Bybit Islamic - no hardcoded coins",
        "count": len(pairs),
        "coins": coins,
        "pairs": pairs
    }, f, indent=2, ensure_ascii=False)
