import mysql.connector
import time
import statistics
import uuid

TESTS = 10
TIMEOUT = 10
POLL_INTERVAL = 0.01

def connect(port):
    return mysql.connector.connect(
        host="127.0.0.1",
        port=port,
        user="root",
        password="root123",
        database="qlsv",
        autocommit=True
    )


master = connect(3307)
replica_1 = connect(3308)
replica_2 = connect(3309)

m = master.cursor()
r1 = replica_1.cursor()
r2 = replica_2.cursor()

latency_1 = []
latency_2 = []


def print_latency_summary(label, latencies):
    if not latencies:
        print(f"{label} samples : 0/{TESTS}")
        print(f"{label} average : N/A ms")
        print(f"{label} median  : N/A ms")
        print(f"{label} min     : N/A ms")
        print(f"{label} max     : N/A ms")
        return

    print(f"{label} samples : {len(latencies)}/{TESTS}")
    print(f"{label} average : {statistics.mean(latencies):.3f} ms")
    print(f"{label} median  : {statistics.median(latencies):.3f} ms")
    print(f"{label} min     : {min(latencies):.3f} ms")
    print(f"{label} max     : {max(latencies):.3f} ms")


for i in range(TESTS):
    ma_sv = "LAT_" + uuid.uuid4().hex[:10]

    m.execute(
        """
        INSERT INTO SinhVien (MaSV, HoTen, NgaySinh)
        VALUES (%s, %s, %s)
        """,
        (
            ma_sv,
            f"Latency Test {i + 1}",
            "2004-01-01"
        )
    )
    start = time.perf_counter()

    t1 = None
    t2 = None

    while time.perf_counter() - start < TIMEOUT:
        if t1 is None:
            r1.execute(
                "SELECT 1 FROM SinhVien WHERE MaSV=%s",
                (ma_sv,)
            )
            if r1.fetchone():
                t1 = (time.perf_counter() - start) * 1000
        if t2 is None:
            r2.execute(
                "SELECT 1 FROM SinhVien WHERE MaSV=%s",
                (ma_sv,)
            )
            if r2.fetchone():
                t2 = (time.perf_counter() - start) * 1000
        if t1 is not None and t2 is not None:
            break

        time.sleep(POLL_INTERVAL)

    if t1 is not None:
        latency_1.append(t1)
    if t2 is not None:
        latency_2.append(t2)

    replica1_value = (
        "N/A" if t1 is None
        else f"{t1:.3f}"
    )
    replica2_value = (
        "N/A" if t2 is None
        else f"{t2:.3f}"
    )

    print(
        f"Test {i + 1:02d} | "
        f"Replica1: {replica1_value} ms | "
        f"Replica2: {replica2_value} ms"
    )

print()
print("REPLICATION LATENCY TEST RESULT")
print()

print_latency_summary(
    "Replica 1",
    latency_1
)

print()

print_latency_summary(
    "Replica 2",
    latency_2
)

m.close()
r1.close()
r2.close()

master.close()
replica_1.close()
replica_2.close()

