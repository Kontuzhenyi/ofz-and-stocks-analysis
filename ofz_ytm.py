from dataclasses import dataclass
from datetime import date


@dataclass
class CashFlow:
    payment_date: date
    amount: float


def year_fraction(start_date: date, end_date: date) -> float:
    return (end_date - start_date).days / 365.0


def present_value(
    yield_rate: float, settle_date: date, cashflows: list[CashFlow]
) -> float:
    total = 0.0
    for flow in cashflows:
        t = year_fraction(settle_date, flow.payment_date)
        total += flow.amount / ((1 + yield_rate) ** t)
    return total


def solve_ytm(price: float, settle_date: date, cashflows: list[CashFlow]) -> float:
    # price рыночная цена облигации
    # Мы приводим стоимость купонов к сегодняшнему дню.
    # Суммируем их стоимость и сравниваем с рыночной ценой.

    # Стартовый диапазон для поиска доходности
    lo = 0.0
    hi = 1.0

    while present_value(hi, settle_date, cashflows) > price:
        hi *= 2
        if hi > 100:
            raise ValueError("Could not bracket the solution for YTM.")

    for _ in range(200):
        mid = (lo + hi) / 2
        pv = present_value(mid, settle_date, cashflows)
        if pv > price:
            lo = mid
        else:
            hi = mid

    return (lo + hi) / 2


def percent(value: float) -> str:
    return f"{value * 100:.2f}%".replace(".", ",")


def money(value: float) -> str:
    return f"{value:,.2f}".replace(",", " ").replace(".", ",")


def print_discount_table(
    yield_rate: float, settle_date: date, cashflows: list[CashFlow]
) -> None:
    print("Дата выплаты | Лет до выплаты | Поток | Приведенная стоимость")
    total = 0.0
    for flow in cashflows:
        t = year_fraction(settle_date, flow.payment_date)
        pv = flow.amount / ((1 + yield_rate) ** t)
        total += pv
        print(
            f"{flow.payment_date.isoformat()} | "
            f"{t:.4f} | "
            f"{money(flow.amount)} | "
            f"{money(pv)}"
        )
    print(f"Сумма PV: {money(total)}")


def main() -> None:
    # Пример для ОФЗ 26235 по данным, которые вы разбирали.
    face_value = 1000.0 # Номинал
    clean_price_percent = 73.16 # % бумаги от номинала
    accrued_interest = 2.4 # НКД
    coupon_value = 29.42 # Сумма купона
    settle_date = date(2026, 4, 2) # Дата покупки облигации

    clean_price = face_value * clean_price_percent / 100
    dirty_price = clean_price + accrued_interest

    # Выплаты купонов
    cashflows = [
        CashFlow(date(2026, 9, 16), coupon_value),
        CashFlow(date(2027, 3, 17), coupon_value),
        CashFlow(date(2027, 9, 15), coupon_value),
        CashFlow(date(2028, 3, 15), coupon_value),
        CashFlow(date(2028, 9, 13), coupon_value),
        CashFlow(date(2029, 3, 14), coupon_value),
        CashFlow(date(2029, 9, 12), coupon_value),
        CashFlow(date(2030, 3, 13), coupon_value),
        CashFlow(date(2030, 9, 11), coupon_value),
        CashFlow(date(2031, 3, 12), coupon_value + face_value),
    ]
    # cashflows = [
    #     CashFlow(date(2026, 5, 20), coupon_value),
    #     CashFlow(date(2026, 11, 20), coupon_value),
    #     CashFlow(date(2027, 5, 20), coupon_value),
    #     CashFlow(date(2027, 11, 20), coupon_value),
    #     CashFlow(date(2028, 5, 17), coupon_value + face_value),
    # ]

    ytm_clean = solve_ytm(clean_price, settle_date, cashflows)
    ytm_dirty = solve_ytm(dirty_price, settle_date, cashflows)

    print("ОФЗ 26235")
    print(f"Чистая цена: {money(clean_price)} руб.")
    print(f"НКД: {money(accrued_interest)} руб.")
    print(f"Грязная цена: {money(dirty_price)} руб.")
    print(f"Купон: {money(coupon_value)} руб.")
    print()
    print(f"Доходность к погашению по чистой цене: {percent(ytm_clean)}")
    print(f"Доходность к погашению по грязной цене: {percent(ytm_dirty)}")
    print()
    print("Дисконтирование потоков по доходности к погашению от чистой цены:")
    print_discount_table(ytm_clean, settle_date, cashflows)


if __name__ == "__main__":
    main()
