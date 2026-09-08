DROP TABLE IF EXISTS sale;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS partner;

CREATE TABLE partner (
    id             SERIAL PRIMARY KEY,
    company_name   VARCHAR(255) NOT NULL,
    inn            VARCHAR(10)  NOT NULL UNIQUE,
    contact_email  VARCHAR(255) UNIQUE,
    phone          VARCHAR(12),
    rating         NUMERIC(2,1)
);

CREATE TABLE product (
    id             SERIAL PRIMARY KEY,
    product_name   VARCHAR(255) NOT NULL
);

CREATE TABLE sale (
    id             SERIAL PRIMARY KEY,
    partner_id     INT NOT NULL,
    product_id     INT NOT NULL,
    sale_date      DATE NOT NULL,
    quantity       SMALLINT NOT NULL CHECK (quantity > 0),
    total_amount   NUMERIC(7,2) NOT NULL CHECK (total_amount >= 0),

    CONSTRAINT fk_sale_partner
        FOREIGN KEY (partner_id)
        REFERENCES partner (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_sale_product
        FOREIGN KEY (product_id)
        REFERENCES product (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);