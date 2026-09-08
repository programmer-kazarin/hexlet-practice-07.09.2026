create table if not exists partners (
	partner_id serial primary key,
	company_name varchar(255),
	inn varchar(10),
	contact_email varchar(255),
	phone varchar(12),
	rating numeric(2,1)
);

create table if not exists sales (
	sale_id serial primary key,
	partner_id int references partners(partner_id),
	product_name varchar(255),
	sale_date date,
	quantity smallint,
	total_amount numeric(7,2)
);

select count(*) from partners; --3
/*
partner_id|company_name           |inn       |contact_email          |phone       |rating|
----------+-----------------------+----------+-----------------------+------------+------+
         1|ООО "Логистик-Экспресс"|7701234567|info@logex.ru          |+79991112233|   4.8|
         2|ИП Петров А.В.         |5001098765|petrov_delivery@mail.ru|            |   4.2|
         3|ТК "Быстрый Путь"      |7812345678|speedway@yandex.ru     |+78125554433|      |
*/

select count(*) from sales; --5
/*
sale_id|partner_id|product_name              |sale_date |quantity|total_amount|
-------+----------+--------------------------+----------+--------+------------+
    101|         1|Стиральный порошок "Альфа"|2026-03-01|      50|    25000.00|
    102|         2|Мыло жидкое "Стандарт"    |2026-03-15|     200|    18000.50|
    103|         1|Кондиционер для белья     |2026-03-20|      30|    10500.00|
    104|         1|Стиральный порошок "Альфа"|2026-03-22|      10|     5000.00|
    105|         3|Мыло жидкое "Стандарт"    |2026-03-25|     150|    13500.00|
*/