import pandas as pd
from pathlib import Path


FILE_NAME = "Прошлые данные - SBER.csv"


def visual(number):
    return round(number * 100, 2)


def load_history_from_csv(file_name: str) -> pd.DataFrame:
    history = pd.read_csv(file_name, sep=";", decimal=",")

    date_col = history.columns[0]
    price_col = history.columns[1]

    history[date_col] = pd.to_datetime(history[date_col], dayfirst=True)
    history[price_col] = pd.to_numeric(history[price_col], errors="coerce")

    history = history.rename(
        columns={
            date_col: "TRADEDATE",
            price_col: "CLOSE",
        }
    )

    history = history.dropna(subset=["TRADEDATE", "CLOSE"])
    history = history.sort_values("TRADEDATE")

    return history


history = load_history_from_csv(FILE_NAME)

# Месячные закрытия: берем последнее значение каждого месяца
monthly = history.set_index("TRADEDATE").resample("ME").last().reset_index()

# Месячная доходность
monthly["return_m"] = monthly["CLOSE"].pct_change(fill_method=None)

# Убираем первый пустой месяц
r = monthly["return_m"].dropna()

# Показатели
avg_monthly = r.mean()
std_monthly = r.std(ddof=1)

annual_expected_arith = avg_monthly * 12
annual_expected_geo = (1 + avg_monthly) ** 12 - 1
annual_risk = std_monthly * (12 ** 0.5)
coef_variation = annual_risk / annual_expected_arith

print("Файл:", Path(FILE_NAME).name)
print("Строк в дневной истории:", len(history))
print("Месячных закрытий:", len(monthly))
print("Ожидаемая годовая доходность:", visual(annual_expected_arith))
print("Геометрическая среднегодовая доходность:", visual(annual_expected_geo))
print("Годовой риск:", visual(annual_risk))
print("Коэффициент вариации:", round(coef_variation, 2))

# Сохранение файлов
# history.to_csv("sber_history_from_csv.csv", index=False, date_format="%Y-%m-%d")
# monthly.to_csv("sber_monthly_from_csv.csv", index=False, date_format="%Y-%m-%d")
