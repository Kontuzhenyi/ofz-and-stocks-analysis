import requests
import pandas as pd
from pathlib import Path

segments = [
    # ("SBER", "EQBR", "2011-01-01", "2013-03-22"),
    ("SBER", "TQBR", "2021-03-25", "2026-03-31"),
]


def fetch_segment(secid, board, date_from, date_to):
    rows = []
    start = 0

    while True:
        
        url = (
            f"https://iss.moex.com/iss/history/engines/stock/markets/shares/"
            f"boards/{board}/securities/{secid}.json"
            f"?from={date_from}&till={date_to}"
            f"&iss.only=history"
            f"&history.columns=TRADEDATE,CLOSE"
            f"&iss.meta=off"
            f"&limit=100"
            f"&start={start}"
        )

        data = requests.get(url, timeout=30).json()
        part = data.get("history", {}).get("data", [])

        if not part:
            break

        rows.extend(part)

        if len(part) < 100:
            break

        start += 100

    df = pd.DataFrame(rows, columns=["TRADEDATE", "CLOSE"])
    if not df.empty:
        df["TRADEDATE"] = pd.to_datetime(df["TRADEDATE"])
        df["CLOSE"] = pd.to_numeric(df["CLOSE"], errors="coerce")
        df["SECID"] = secid
        df["BOARD"] = board
        df = df.sort_values("TRADEDATE")

    return df

def vizual(number):
    return round(number*100, 2)
    

parts = [fetch_segment(*segment) for segment in segments]
history = pd.concat(parts, ignore_index=True).sort_values("TRADEDATE")

# Месячные закрытия: берем последнее значение каждого месяца
monthly = history.set_index("TRADEDATE").resample("ME").last().reset_index()

# Месячная доходность
monthly["return_m"] = monthly["CLOSE"].pct_change()

# Убираем первый пустой месяц
r = monthly["return_m"].dropna()

# Показатели
avg_monthly = r.mean()
std_monthly = r.std(ddof=1)

annual_expected_arith = avg_monthly * 12
annual_expected_geo = (1 + avg_monthly) ** 12 - 1
annual_risk = std_monthly * (12 ** 0.5)
coef_variation = annual_risk / annual_expected_arith

# print("Средняя месячная доходность:", round(avg_monthly*100, 2))
print("Ожидаемая годовая доходность:", vizual(annual_expected_arith))
# print("Геометрическая среднегодовая доходность:", round(annual_expected_geo*100, 2))
print("Годовой риск:", vizual(annual_risk))
print("Коэффициент вариации:", round(coef_variation, 2))

# Сохранение файлов
# history.to_csv("test.csv", index=False, date_format="%Y-%m-%d")
# monthly.to_csv("stocks_mtss_monthly.csv", index=False, date_format="%Y-%m-%d")
