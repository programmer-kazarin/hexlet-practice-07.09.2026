# db.py
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

EMAIL_UNIQUE_CONSTRAINT = "uq_partners_email"


class PartnerNotFoundError(Exception):
    """Партнер с указанным ID не найден в БД."""
    pass


class DuplicateInnError(Exception):
    """Партнер с таким ИНН уже существует (нарушение уникальности)."""
    pass


class DuplicateEmailError(Exception):
    """Партнер с таким email уже существует (нарушение уникальности)."""
    pass


class DatabaseUnavailableError(Exception):
    """СУБД недоступна: сервер БД не отвечает или отсутствует сеть."""
    pass


def _connect():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.OperationalError as connection_error:
        raise DatabaseUnavailableError(
            "Не удалось подключиться к базе данных"
        ) from connection_error


def _translate_unique_violation(error: psycopg2.errors.UniqueViolation, data: dict):
    """Определяет по имени ограничения, какое именно поле дублируется."""
    constraint_name = getattr(error.diag, "constraint_name", None)
    if constraint_name == EMAIL_UNIQUE_CONSTRAINT:
        return DuplicateEmailError(
            f"Партнер с email {data.get('contact_email')} уже существует"
        )
    return DuplicateInnError(f"Партнер с ИНН {data.get('inn')} уже существует")


def fetch_partners_raw():
    query = """
        SELECT
            p.partner_id,
            p.company_name,
            p.partner_type,
            p.inn,
            p.address,
            p.director_name,
            p.contact_email,
            p.phone,
            p.rating,
            COALESCE(SUM(d.quantity), 0) AS total_quantity
       FROM partners p
       LEFT JOIN deliveries d ON d.partner_id = p.partner_id
      GROUP BY p.partner_id, p.company_name, p.partner_type, p.inn,
               p.address, p.director_name, p.contact_email, p.phone, p.rating
      ORDER BY p.company_name;
    """
    conn = None
    try:
        conn = _connect()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            return cursor.fetchall()
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


def get_partner_by_id(partner_id: int) -> dict:
    query = """
        SELECT partner_id, company_name, partner_type, inn, address,
               director_name, contact_email, phone, rating
          FROM partners
         WHERE partner_id = %s;
    """
    conn = None
    try:
        conn = _connect()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (partner_id,))
            row = cursor.fetchone()
            if row is None:
                raise PartnerNotFoundError(f"Партнер с ID={partner_id} не найден")
            return dict(row)
    finally:
        if conn is not None:
            conn.close()


def get_partner_sales_history(partner_id: int) -> dict:
    """История реализации продукции партнера.
    """
    partner_query = "SELECT company_name FROM partners WHERE partner_id = %s;"
    history_query = """
        SELECT pr.product_name,
               d.quantity,
               TO_CHAR(d.delivery_date, 'DD.MM.YYYY') AS sale_date
          FROM deliveries d
          JOIN products pr ON pr.product_id = d.product_id
         WHERE d.partner_id = %s
         ORDER BY d.delivery_date DESC, d.delivery_id DESC;
    """
    conn = None
    try:
        conn = _connect()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(partner_query, (partner_id,))
            partner_row = cursor.fetchone()
            if partner_row is None:
                raise PartnerNotFoundError(f"Партнер с ID={partner_id} не найден")

            cursor.execute(history_query, (partner_id,))
            sales = [dict(row) for row in cursor.fetchall()]

        return {
            "partner_id": partner_id,
            "company_name": partner_row["company_name"],
            "sales": sales,
            "total_quantity": sum(sale["quantity"] for sale in sales),
        }
    finally:
        if conn is not None:
            conn.close()


def create_partner(data: dict) -> int:
    query = """
        INSERT INTO partners
            (company_name, partner_type, inn, address, director_name, contact_email, phone, rating)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING partner_id;
    """
    conn = None
    try:
        conn = _connect()
        with conn.cursor() as cursor:
            cursor.execute(query, (
                data["company_name"],
                data["partner_type"],
                data["inn"],
                data["address"],
                data["director_name"],
                data["contact_email"],
                data["phone"],
                data["rating"],
            ))
            new_id = cursor.fetchone()[0]
        conn.commit()
        return new_id
    except psycopg2.errors.UniqueViolation as unique_error:
        conn.rollback()
        raise _translate_unique_violation(unique_error, data) from unique_error
    except psycopg2.OperationalError as connection_error:
        raise DatabaseUnavailableError(
            "Не удалось подключиться к базе данных"
        ) from connection_error
    except Exception:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()


def update_partner(partner_id: int, data: dict) -> None:
    get_partner_by_id(partner_id)  # бросит PartnerNotFoundError, если записи нет

    query = """
        UPDATE partners
           SET company_name = %s,
               partner_type = %s,
               inn = %s,
               address = %s,
               director_name = %s,
               contact_email = %s,
               phone = %s,
               rating = %s
         WHERE partner_id = %s;
    """
    conn = None
    try:
        conn = _connect()
        with conn.cursor() as cursor:
            cursor.execute(query, (
                data["company_name"],
                data["partner_type"],
                data["inn"],
                data["address"],
                data["director_name"],
                data["contact_email"],
                data["phone"],
                data["rating"],
                partner_id,
            ))
        conn.commit()
    except psycopg2.errors.UniqueViolation as unique_error:
        conn.rollback()
        raise _translate_unique_violation(unique_error, data) from unique_error
    except psycopg2.OperationalError as connection_error:
        raise DatabaseUnavailableError(
            "Не удалось подключиться к базе данных"
        ) from connection_error
    except Exception:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()