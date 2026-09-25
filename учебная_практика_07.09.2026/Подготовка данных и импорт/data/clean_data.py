import pandas as pd
import re
from datetime import datetime

# ---------- 1. Очистка партнёров ----------
partners_raw = pd.read_csv('import_partners.csv', dtype=str)

# Убираем пробелы, но НЕ трогаем NaN здесь
for col in ['company_name', 'inn', 'contact_email', 'phone']:
    partners_raw[col] = partners_raw[col].apply(
        lambda x: x.strip() if isinstance(x, str) else x
    )
    # заменяем пустые строки на настоящий NaN
    partners_raw[col] = partners_raw[col].replace('', pd.NA)

partners_raw['partner_id'] = partners_raw['partner_id'].astype(int)
partners_raw['rating'] = pd.to_numeric(partners_raw['rating'], errors='coerce')

def normalize_phone(phone):
    if pd.isna(phone):          # <-- ключевое исправление
        return None
    digits = re.sub(r'[^\d+]', '', str(phone))
    return digits or None

partners_raw['phone'] = partners_raw['phone'].apply(normalize_phone)

def valid_inn(inn):
    if pd.isna(inn):
        return False
    return bool(re.fullmatch(r'\d{10}|\d{12}', str(inn)))

partners_raw['inn_valid'] = partners_raw['inn'].apply(valid_inn)
print("Некорректные ИНН:\n", partners_raw[~partners_raw['inn_valid']])

partners_clean = partners_raw[partners_raw['inn_valid']].drop(columns=['inn_valid'])
partners_clean = partners_clean.drop_duplicates(subset=['inn'], keep='first')

# rating и contact_email могут быть NaN -> для CSV это нормально (пустая ячейка)
partners_clean.to_csv('partners_clean.csv', index=False)
print(f"Партнёров после очистки: {len(partners_clean)}")

# ---------- 2. Очистка отгрузок ----------
sales_raw = pd.read_csv('import_sales.txt', sep='\t', dtype=str)
sales_raw['product_name'] = sales_raw['product_name'].str.strip()
sales_raw['sale_id']      = sales_raw['sale_id'].astype(int)
sales_raw['partner_id']   = sales_raw['partner_id'].astype(int)
sales_raw['quantity']     = sales_raw['quantity'].astype(int)
sales_raw['total_amount'] = sales_raw['total_amount'].astype(float)

def parse_date(value):
    if pd.isna(value):
        return None
    for fmt in ('%Y-%m-%d', '%d.%m.%Y'):
        try:
            return datetime.strptime(str(value), fmt).date()
        except ValueError:
            continue
    return None

sales_raw['sale_date'] = sales_raw['sale_date'].apply(parse_date)
sales_raw = sales_raw.dropna(subset=['sale_date'])

# Проверка ссылочной целостности
valid_ids = set(partners_clean['partner_id'])
orphans = sales_raw[~sales_raw['partner_id'].isin(valid_ids)]
if not orphans.empty:
    print("Отгрузки с несуществующим партнёром (исключены):\n", orphans)
    orphans.to_csv('sales_orphans.csv', index=False)

sales_clean = sales_raw[sales_raw['partner_id'].isin(valid_ids)].copy()
sales_clean = sales_clean.drop_duplicates(subset=['sale_id'], keep='first')

# ---------- 3. Справочник продуктов (нормализация 3NF) ----------
unique_products = sorted(sales_clean['product_name'].unique())
products_clean = pd.DataFrame({
    'product_id': range(1, len(unique_products) + 1),
    'product_name': unique_products
})
products_clean.to_csv('products_clean.csv', index=False)

name_to_id = dict(zip(products_clean['product_name'], products_clean['product_id']))
sales_clean['product_id'] = sales_clean['product_name'].map(name_to_id)

deliveries_clean = sales_clean.rename(
    columns={'sale_id': 'delivery_id', 'sale_date': 'delivery_date'}
)[['delivery_id', 'partner_id', 'product_id', 'delivery_date', 'quantity', 'total_amount']]

deliveries_clean.to_csv('deliveries_clean.csv', index=False)
print(f"Продуктов: {len(products_clean)}, отгрузок: {len(deliveries_clean)}")