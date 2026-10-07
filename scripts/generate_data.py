from faker import Faker
import mysql.connector
import time

fake = Faker("vi_VN")

my_connector = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="root123",
    database="qlsv",
)

cursor = my_connector.cursor()

sql = """
INSERT INTO SinhVien (MaSV, HoTen, NgaySinh)
VALUES (%s, %s, %s)
"""

rows = []

for i in range(1, 10001):
    rows.append((
        f"FAKESV{i:05d}",
        fake.name(),
        fake.date_between(
            start_date="-25y",
            end_date="-18y",
        )
    ))

start = time.perf_counter()

cursor.executemany(sql, rows)
my_connector.commit()

elapsed = time.perf_counter() - start

print("DATA GENERATION")
print(f"Inserted rows: {len(rows)}")
print(f"Time elapsed: {elapsed} seconds")

cursor.close()
my_connector.close()