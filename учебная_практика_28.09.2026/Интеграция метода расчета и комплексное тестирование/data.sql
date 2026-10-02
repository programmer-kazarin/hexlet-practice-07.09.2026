-- запускать один раз после schema.sql
INSERT INTO partners
    (company_name, partner_type, inn, address, director_name, contact_email, phone, rating)
VALUES
    ('ООО Ромашка', 'ООО', '7701234567', 'г. Москва, ул. Ленина, 1',
     'Иванов Иван Иванович', 'info@romashka.ru', '+7 (495) 123-45-67', 5),
    ('ИП Петров', 'ИП', '770123456789', 'г. Тверь, ул. Садовая, 5',
     'Петров Петр Петрович', 'petrov@mail.ru', '+7 (482) 222-33-44', 3)
ON CONFLICT DO NOTHING;

INSERT INTO products (product_name, unit_price) VALUES
    ('Доска паркетная', 1200.00),
    ('Ламинат 33 класс', 650.00),
    ('Плинтус напольный', 150.00)
ON CONFLICT DO NOTHING;

INSERT INTO deliveries (partner_id, product_id, delivery_date, quantity, total_amount)
SELECT p.partner_id, pr.product_id, v.delivery_date, v.quantity, v.quantity * pr.unit_price
  FROM (VALUES
        ('7701234567',   'Ламинат 33 класс',  DATE '2026-03-15', 12000),
        ('7701234567',   'Доска паркетная',   DATE '2026-05-02', 40000),
        ('7701234567',   'Плинтус напольный', DATE '2026-09-20',  8500),
        ('770123456789', 'Ламинат 33 класс',  DATE '2026-07-11',  3000)
       ) AS v(inn, product_name, delivery_date, quantity)
  JOIN partners p  ON p.inn = v.inn
  JOIN products pr ON pr.product_name = v.product_name;

INSERT INTO product_types (type_name, coefficient) VALUES
    ('Ламинат',          2.5000),
    ('Паркетная доска',  4.3500),
    ('Плинтус',          1.1000)
ON CONFLICT DO NOTHING;

INSERT INTO material_types (material_name, defect_percent) VALUES
    ('Древесина',        0.50),
    ('Пластик',          0.30),
    ('Металл',           0.00)
ON CONFLICT DO NOTHING;