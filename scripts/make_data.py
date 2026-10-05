"""สร้างข้อมูลจำลองของ WattWise (seed คงที่) -> data/*.csv และ dashboard/data.js
สมมติฐานราคา/สัดส่วน อ้างอิงสไลด์ 4P ของกลุ่ม; ตัวเลขการใช้ไฟเป็นข้อมูลจำลองทั้งหมด"""
import csv, json, random, datetime as dt, pathlib
random.seed(67)
R = pathlib.Path(__file__).resolve().parent.parent
TARIFF, HW_PRICE, HW_COGS, SUB_BAHT, ATTACH = 4.2, 3500, 1800, 149, 0.40  # บาท/หน่วย, บาท, บาท, บาท/เดือน, สัดส่วน
AP = {"แอร์": 9.0, "ตู้เย็น": 1.6, "เครื่องทำน้ำอุ่น": 2.2, "เครื่องซักผ้า": 0.9, "ไฟส่องสว่าง": 1.1, "อื่นๆ": 1.8}  # kWh/วัน

start = dt.date(2026, 9, 5); dates, daily = [], {a: [] for a in AP}
for i in range(30):
    dates.append((start + dt.timedelta(i)).isoformat())
    for a, b in AP.items():
        k = b * random.uniform(.85, 1.15)
        if a == "แอร์" and i >= 20: k *= 1 + 0.025 * (i - 19)  # คอมเพรสเซอร์เสื่อม: ใช้ไฟเพิ่มทีละน้อย
        daily[a].append(round(k, 2))
with open(R/"data/appliance_daily.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["date", "appliance", "kwh"])
    for i, d in enumerate(dates):
        for a in AP: w.writerow([d, a, daily[a][i]])

def prof(a, h):
    return {"แอร์": 0.9 if h >= 22 or h < 6 else 0.6 if 12 <= h < 17 else 0.05, "ตู้เย็น": 0.07,
            "เครื่องทำน้ำอุ่น": 1.2 if h in (6, 7, 19, 20) else 0, "เครื่องซักผ้า": 0.5 if h in (10, 11) else 0,
            "ไฟส่องสว่าง": 0.15 if 18 <= h <= 23 else 0.01, "อื่นๆ": 0.08}[a]
hourly = {a: [round(prof(a, h) * random.uniform(.9, 1.1), 3) for h in range(24)] for a in AP}
with open(R/"data/hourly_profile.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["hour", "appliance", "kw"])
    for h in range(24):
        for a in AP: w.writerow([h, a, hourly[a][h]])

biz, cum = [], 0
for y, (new, fixed, ins) in enumerate([(1000, 2.5e6, 0), (2500, 3.0e6, 1.5e5), (4500, 4.0e6, 6e5)], 1):
    hw = new * HW_PRICE; subs = ATTACH * (cum + new / 2) * SUB_BAHT * 12; inst = 0.15 * new * 800
    rev = hw + subs + inst + ins; cost = new * HW_COGS + fixed + 0.15 * rev; cum += new
    biz.append(dict(year=y, units=new, hardware=round(hw), saas=round(subs), install=round(inst), insights=ins,
                    revenue=round(rev), cost=round(cost), profit=round(rev - cost)))
with open(R/"data/business_projection.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, biz[0].keys()); w.writeheader(); w.writerows(biz)

js = dict(tariff=TARIFF, hw=HW_PRICE, names=list(AP), dates=dates, daily=daily, hourly=hourly, biz=biz)
(R/"dashboard/data.js").write_text("window.DATA=" + json.dumps(js, ensure_ascii=False) + ";", encoding="utf-8")
print("ok", [b["profit"] for b in biz])
