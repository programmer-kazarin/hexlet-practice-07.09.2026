create table if not exists partner (
	id serial primary key,
	company_name varchar(255),
	inn varchar(10) not null unique,
	contact_email varchar(255) unique,
	phone varchar(12),
	rating numeric(2,1)
);

create table if not exists product (
	id serial primary key,
	product_name varchar(255) not null
);

create table if not exists sale (
	id serial primary key,
	partner_id int references partner(id) not null,
	product_id int references product(id) not null,
	sale_date date not null,
	quantity smallint not null,
	total_amount numeric(7,2) not null
);