from datetime import date
from dateutil.relativedelta import relativedelta

d = date(2026, 5, 20)
new_d = d
for i in range(4):
    new_d += relativedelta(months=6)
    print(new_d)

# print(new_d)  # 2026-10-07