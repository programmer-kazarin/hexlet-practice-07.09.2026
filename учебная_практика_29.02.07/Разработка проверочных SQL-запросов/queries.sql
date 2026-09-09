-- Запрос для вывода списка партнеров 
SELECT
    p.partner_id,
    p.company_name,
    p.inn,
    COUNT(d.delivery_id) AS total_deliveries
FROM partners p
LEFT JOIN deliveries d ON d.partner_id = p.partner_id
GROUP BY p.partner_id, p.company_name, p.inn
ORDER BY p.company_name ASC;
/*
partner_id|company_name           |inn       |total_deliveries|
----------+-----------------------+----------+----------------+
         2|ИП Петров А.В.         |5001098765|               1|
         1|ООО "Логистик-Экспресс"|7701234567|               2|
         3|ТК "Быстрый Путь"      |7812345678|               1|
*/


-- Запрос для добавления/обновления данных 
BEGIN;

INSERT INTO partners (company_name, inn, contact_email, phone, rating)
VALUES ('ООО "Новый Партнер"', '7700000000', 'new_partner@example.com',
        '+79000000000', 5.0);

INSERT INTO products (product_name, unit_price)
VALUES ('Тестовый продукт', 100.00)
ON CONFLICT (product_name) DO NOTHING;

INSERT INTO deliveries (partner_id, product_id, delivery_date, quantity, total_amount)
VALUES (
    (SELECT partner_id FROM partners WHERE inn = '7700000000'),
    (SELECT product_id FROM products WHERE product_name = 'Тестовый продукт'),
    CURRENT_DATE,
    1,
    100.00
);

COMMIT;
/* 
результат в папке screenshots
*/


-- Детальная история отгрузок
SELECT
    pr.company_name,
    pd.product_name,
    d.delivery_date,
    d.quantity,
    d.total_amount
FROM deliveries d
JOIN partners pr ON pr.partner_id = d.partner_id
JOIN products pd ON pd.product_id = d.product_id
WHERE d.partner_id = 1
  AND d.delivery_date BETWEEN '2026-03-01' AND '2026-03-31'
ORDER BY d.delivery_date;
/*
После инсертов выше
company_name           |product_name              |delivery_date|quantity|total_amount|
-----------------------+--------------------------+-------------+--------+------------+
ООО "Логистик-Экспресс"|Стиральный порошок "Альфа"|   2026-03-01|      50|    25000.00|
ООО "Логистик-Экспресс"|Кондиционер для белья     |   2026-03-20|      30|    10500.00|
*/

-- Итоговая сумма поставки
SELECT
    SUM(d.quantity)     AS period_total_quantity,
    SUM(d.total_amount) AS period_total_amount
FROM deliveries d
WHERE d.partner_id = 1
  AND d.delivery_date BETWEEN '2026-03-01' AND '2026-03-31';
/*
После инсертов выше
period_total_quantity|period_total_amount|
---------------------+-------------------+
                   80|           35500.00|
*/