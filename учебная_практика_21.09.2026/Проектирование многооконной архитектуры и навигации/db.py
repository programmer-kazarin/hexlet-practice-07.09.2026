import psycopg2
from psycopg2.extras import RealDictCursor
from discount import calculate_partner_discount

DB_CONFIG = {
    "host": "localhost",
    "port": 5435,
    "dbname": "test_db_kazarin",
    "user": "postgres",
    "password": "postgres",
}


def fetch_partners_raw():    
    query = """
        SELECT
            p.partner_id,
            p.company_name,
            p.inn,
            p.contact_email,
            p.phone,
            p.rating,
            COALESCE(SUM(d.quantity), 0) AS total_quantity
       FROM partners p
       LEFT JOIN deliveries d ON d.partner_id = p.partner_id
      GROUP BY p.partner_id, p.company_name, p.inn, p.contact_email, p.phone, p.rating
      ORDER BY p.company_name;
    """
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    except psycopg2.Error as db_error:
        print(f"Ошибка подключения к БД: {db_error}")
        return []
    finally:
        if conn is not None:
            conn.close()


def get_partners_with_discount():
    raw_rows = fetch_partners_raw()
    partners_with_discount = []

    for row in raw_rows:
        total_quantity = row["total_quantity"] or 0
        discount_percent = calculate_partner_discount(total_quantity)

        partner_data = dict(row)
        partner_data["discount_percent"] = discount_percent
        partners_with_discount.append(partner_data)

    return partners_with_discount