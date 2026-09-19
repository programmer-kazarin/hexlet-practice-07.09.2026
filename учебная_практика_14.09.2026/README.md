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

## Интеграция с БД и агрегация данных (SQL + Backend)
* discount.py скопировал из предыдущего задания
* Схема БД с данными взяты взята из "учебная_практика_29.02.07"
	- вместо sales_history у меня deliveries
``` bash
# установка библиотеки psycopg2
pip install psycopg2-binary

```

## Разработка интерфейса (UI) по руководству по стилю
### Запуск интерфейса
* Открыть в браузере templates/index.html (скриншот в папке screenshots)
* Партнеры пока захардкожены в html