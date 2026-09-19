# Учебная практика 14.09.2026
## Разработка ядра бизнес-логики (Расчет скидки)
``` bash
cd Разработка\ ядра\ бизнес-логики

# Запуск тестов
python test_discount.py

# Проверка покрытия
pip install coverage
coverage run -m unittest test_discount.py
coverage report -m
# Name               Stmts   Miss  Cover   Missing
# ------------------------------------------------
# discount.py           12      0   100%
# test_discount.py      25      1    96%   39
# ------------------------------------------------
# TOTAL                 37      1    97%
```