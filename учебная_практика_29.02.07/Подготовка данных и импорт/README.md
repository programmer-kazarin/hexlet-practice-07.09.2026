1. В папке data находится скрипт clean_data.py и файлы с данными, которые нужно очистить перед импортом.
2. Запуск скрипта:
``` bash
$ python clean_data.py 
```
3. результат работы скрипта:
``` bash
Некорректные ИНН:
 Empty DataFrame
Columns: [partner_id, company_name, inn, contact_email, phone, rating, inn_valid]
Index: []
Партнёров после очистки: 3
Отгрузки с несуществующим партнёром (исключены):
    sale_id  partner_id                product_name   sale_date  quantity  total_amount
3      104           4  Стиральный порошок "Альфа"  2026-03-22        10        5000.0
Продуктов: 3, отгрузок: 4
```
На выходе 3 файла для импорта: partners_clean.csv, products_clean.csv, deliveries_clean.csv.
И один файл sales_orphans.csv с записями, не прошедшими проверку на ссылочную целостность.

4. Проверочные запросы:
``` sql
SELECT COUNT(*) AS partners_count   FROM partners;    -- ожидается 3
SELECT COUNT(*) AS products_count   FROM products;     -- ожидается 3
SELECT COUNT(*) AS deliveries_count FROM deliveries;   -- ожидается 4
```

5. В папке screenshots скрины загрузки через импорт DBeaver и их результаты. 