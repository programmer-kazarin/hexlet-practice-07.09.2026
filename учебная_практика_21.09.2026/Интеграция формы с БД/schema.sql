DROP TABLE IF EXISTS deliveries;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS partners;

CREATE TABLE partners (
    partner_id      SERIAL PRIMARY KEY,
    company_name    VARCHAR(255)    NOT NULL,
    inn             VARCHAR(12)     NOT NULL,
    contact_email   VARCHAR(255),
    phone           VARCHAR(30),
    rating          DECIMAL(3,2),
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_partners_inn   UNIQUE (inn),
    CONSTRAINT uq_partners_email UNIQUE (contact_email)
);

CREATE TABLE products (
    product_id      SERIAL PRIMARY KEY,
    product_name    VARCHAR(255)    NOT NULL,
    unit_price      DECIMAL(10,2),
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_products_name UNIQUE (product_name)
);

CREATE TABLE deliveries (
    delivery_id     SERIAL PRIMARY KEY,
    partner_id      INT             NOT NULL,
    product_id      INT             NOT NULL,
    delivery_date   DATE            NOT NULL,
    quantity        INT             NOT NULL CHECK (quantity > 0),
    total_amount    DECIMAL(12,2)   NOT NULL CHECK (total_amount >= 0),
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_deliveries_partner
        FOREIGN KEY (partner_id) REFERENCES partners(partner_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_deliveries_product
        FOREIGN KEY (product_id) REFERENCES products(product_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_deliveries_partner_id ON deliveries(partner_id);
CREATE INDEX idx_deliveries_product_id ON deliveries(product_id);
CREATE INDEX idx_deliveries_date       ON deliveries(delivery_date);


ALTER TABLE partners ADD COLUMN IF NOT EXISTS partner_type VARCHAR(10);
ALTER TABLE partners ADD COLUMN IF NOT EXISTS address VARCHAR(255);
ALTER TABLE partners ADD COLUMN IF NOT EXISTS director_name VARCHAR(150);
ALTER TABLE partners ADD CONSTRAINT partners_inn_unique UNIQUE (inn);