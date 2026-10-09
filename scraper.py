import json, time, re
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    page = browser.new_page(user_agent="Mozilla/5.0 Chrome/122.0")

    all_mubah = set()
    api_data = []

    # كنصنتو للـ API اللي كيجيب البيانات
    def handle_response(resp):
        try:
            url = resp.url
            if "api" in url or "report" in url or "currenc" in url or "data" in url:
                if "json" in resp.headers.get("content-type",""):
                    try:
                        j = resp.json()
                        api_data.append((url, j))
                        print(f"API FOUND: {url} -> {str(j)[:200]}")
                    except: pass
        except: pass

    page.on("response", handle_response)

    # 1 - جرب الصفحة الرئيسية
    print("Going to /ar")
    page.goto("https://cryptohalal.cc/ar", timeout=90000, wait_until="networkidle")
    page.wait_for_timeout(8000)

    # 2 - جرب صفحة التقارير
    for url in ["https://cryptohalal.cc/ar/reports", "https://cryptohalal.cc/reports", "https://cryptohalal.cc/ar/currencies", "https://cryptohalal.cc/api/currencies"]:
        try:
            print(f"Trying {url}")
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(6000)
            # شوف واش كاين جدول
            rows = page.locator("table tr").all()
            print(f"{url} rows {len(rows)}")
            if len(rows) > 15:
                # لقينا الصفحة اللي فيها بزاف
                break
        except Exception as e:
            print(f"{url} err {e}")

    # 3 - قلبو الـ select ديال 10/25/100 باش يورينا 100 فالصفحة
    try:
        sel = page.locator("select[name*='length'], select.form-select, select:has(option:has-text('100'))").first
        if sel.count() > 0:
            print("Found length select, setting to 100")
            sel.select_option(label="100")
            page.wait_for_timeout(5000)
            # ولا All
            try:
                sel.select_option(value="100")
                page.wait_for_timeout(5000)
            except: pass
    except Exception as e:
        print(f"Select err {e}")

    # 4 - دابا جمع كلشي مباح من الجدول الحالي + من الـ API
    rows = page.locator("table tr").all()
    print(f"FINAL ROWS {len(rows)}")
    for row in rows:
        try:
            txt = row.inner_text()
            if "مباح" in txt and "غير مباح" not in txt:
                syms = re.findall(r'\b[A-Z]{2,10}\b', txt)
                for s in syms:
                    if s.isalpha() and s not in ["USDT","USDC","EUR","USD","AR"] and len(s)>=2 and len(s)<=10:
                        if s not in ["TRON"]: # TRON = TRX
                            # TRON خاصو يولي TRX
                            if s=="TRON":
                                all_mubah.add("TRX")
                            else:
                                all_mubah.add(s)
                        else:
                            all_mubah.add("TRX")
        except: pass

    # 5 - إلا لقينا API فيه بيانات، استعملوه
    for url, data in api_data:
        try:
            # data ممكن يكون list ديال العملات
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        status = str(item.get("status","") + item.get("ruling","") + item.get("halal","")).lower()
                        if "مباح" in status or "halal" in status or item.get("is_halal")==True:
                            sym = item.get("symbol") or item.get("code") or item.get("ticker")
                            if sym:
                                all_mubah.add(sym.upper())
            elif isinstance(data, dict):
                # شوف الداخل
                for k,v in data.items():
                    if isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict) and "مباح" in str(item):
                                sym = item.get("symbol")
                                if sym:
                                    all_mubah.add(sym.upper())
        except: pass

    browser.close()

    # نظف TRON
    if "TRON" in all_mubah:
        all_mubah.discard("TRON")
        all_mubah.add("TRX")

    merged = sorted(list(all_mubah))
    print(f"FINAL CH LIVE {len(merged)} مباح: {merged}")
    print(f"APIs found: {len(api_data)}")

    with open("halal_pairs.json","w",encoding="utf-8") as f:
        json.dump({
            "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
            "live": True,
            "source": f"LIVE cryptohalal.cc - {len(merged)} مباح - scanned reports + API",
            "count": len(merged),
            "coins": merged,
            "pairs": [f"{c}/USDT" for c in merged],
            "debug_apis": [u for u,_ in api_data][:5]
        }, f, indent=2, ensure_ascii=False)
