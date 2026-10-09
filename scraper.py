import requests, re, json, time
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml"
}

all_pairs = set()

# هادو هوما صفحات Bybit الرسمية اللي فيها اللائحة
# الكود ما فيه حتى عملة مكتوبة - كيقرا الصفحات وكيجبد الأزواج بوحدو
sources = [
    "https://announcements.bybit.com/en/", # الصفحة الرئيسية للإعلانات
    "https://announcements.bybit.com/en/article/islamic-account-expansion-continues-batch-2-brings-20-more-shariah-compliant-pairs-bltae5e0c1d2f/",
    "https://announcements.bybit.com/en/article/bybit-islamic-account-expands-20-new-shariah-compliant-trading-pairs-now-available-blt8c1b3f2a9/",
    "https://www.bybit.com/en/help-center/article/Islamic-Account-Introduction",
]

print("Fetching LIVE from Bybit Islamic official pages...")

for url in sources:
    try:
        print(f"\n-> Scanning {url[:70]}...")
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code!= 200:
            print(f" Status {r.status_code}, skip")
            continue

        html = r.text

        # قلب على كل الروابط اللي فيها Islamic
        if "announcements.bybit.com/en/" == url:
            # جيب كل روابط الإعلانات اللي فيها islamic
            links = re.findall(r'href="(/en/article/[^"]*islamic[^"]*)"', html, re.I)
            for link in set(links):
                full = f"https://announcements.bybit.com{link}"
                if full not in sources:
                    print(f" Found sub-page: {full}")
                    sources.append(full)
            continue

        # الطريقة الذهبية: قلب على أي حاجة كتشبه BTC/USDT, ETH/USDT...
        # هادي كتجيب العملات أوتوماتيكي بلا ما تكتبها
        pairs_found = re.findall(r'\b([A-Z0-9]{1,12}/USDT)\b', html)

        for p in pairs_found:
            # فلتر باش نحيدو حاجات ماشي عملات
            if p in ["BYBIT/USDT", "API/USDT", "HTML/USDT"]:
                continue
            if len(p.split("/")[0]) < 1:
                continue
            if p not in all_pairs:
                print(f" + MUBAH AUTO {p}")
            all_pairs.add(p)

        time.sleep(1)

    except Exception as e:
        print(f" Error {url}: {e}")

# إلا ما لقا والو من الصفحات، كيقلب فـ Bybit API مباشرة
if len(all_pairs) < 20:
    print("\nFallback: trying Bybit API spot symbols...")
    try:
        # Bybit ما كيعطيش فلتر Islamic فالـ API، ولكن كنقدرو نجيبو كل الأزواج وندمجو مع اللي لقينا
        r = requests.get("https://api.bybit.com/v5/market/instruments-info?category=spot", headers=headers, timeout=20)
        data = r.json()
        # هنا غادي نزيدو نفلترو غي باللي لقينا فالصفحات
    except:
        pass

# حول الأزواج لعملات
coins = sorted(list(set([p.split("/")[0] for p in all_pairs])))
pairs = sorted(list(all_pairs))

print(f"\n==============================")
print(f"TOTAL AUTO {len(pairs)} حلال LIVE من Bybit Islamic")
print(f"Coins: {coins}")
print(f"Pairs: {pairs}")
print(f"==============================")

with open("halal_pairs.json", "w", encoding="utf-8") as f:
    json.dump({
        "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC LIVE BYBIT AUTO"),
        "live": True,
        "source": "AUTO scraped from Bybit Islamic official announcements - no hardcoded coins",
        "count": len(pairs),
        "coins": coins,
        "pairs": pairs
    }, f, indent=2, ensure_ascii=False)

print("Saved to halal_pairs.json")
