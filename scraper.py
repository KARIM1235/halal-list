import json, time, re
from playwright.sync_api import sync_playwright

all_coins = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(user_agent="Mozilla/5.0 Chrome/122.0")

    def handle_response(resp):
        url = resp.url
        # أي API فيه coins
        if "coin" in url.lower() and "api" in url.lower():
            try:
                data = resp.json()
                # نحاولو نستخرجو الـ items
                items = []
                if isinstance(data, dict):
                    if isinstance(data.get("data"), list):
                        items = data["data"]
                    elif isinstance(data.get("data"), dict):
                        items = data["data"].get("items") or data["data"].get("data") or []
                    else:
                        items = data.get("items") or []
                elif isinstance(data, list):
                    items = data

                for c in items:
                    if isinstance(c, dict):
                        sym = (c.get("symbol") or "").upper()
                        if sym:
                            all_coins[sym] = c
                            # print للـ debug
                            j = c.get("judgement", c.get("judgment", c.get("status")))
                            print(f"Captured {sym} j={j} from {url[:70]}")

            except Exception as e:
                pass

    page.on("response", handle_response)

    print("Loading https://cryptohalal.cc/ar")
    page.goto("https://cryptohalal.cc/ar", wait_until="networkidle", timeout=60000)
    time.sleep(5)

    # نـscrollيو باش نجيبو كل 131 عملة
    # الموقع كيدير infinite scroll كيعمر 10 بـ 10
    for i in range(15): # 15 مرة scroll = 150 عملة
        page.mouse.wheel(0, 3000)
        time.sleep(2)
        print(f"Scroll {i+1}/15 -> collected {len(all_coins)} coins")

    browser.close()

# دابا نفلترو غير مباح
mubah = []
for sym, c in all_coins.items():
    j = c.get("judgement")
    if j is None: j = c.get("judgment")
    if j is None: j = c.get("status")
    if j is None: j = c.get("hukm")

    is_mubah = False
    if isinstance(j, int) and j == 0: is_mubah = True
    if isinstance(j, str) and ("مباح" in j or j=="0" or j.lower()=="halal"): is_mubah = True
    if c.get("is_halal") == True: is_mubah = True

    if is_mubah:
        mubah.append(sym)

mubah = sorted(list(set(mubah)))
print(f"\nFINAL {len(mubah)} مباح LIVE from NEW API: {mubah}")
print(f"TOTAL collected {len(all_coins)} coins")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE NEW"),
        "live": True,
        "source": f"LIVE NEW cryptohalal.cc scroll - {len(all_coins)} total, {len(mubah)} halal",
        "count": len(mubah),
        "coins": mubah,
        "pairs": [f"{c}/USDT" for c in mubah]
    }, f, indent=2, ensure_ascii=False)
