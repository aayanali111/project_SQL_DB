import time
from multiprocessing import Pool, cpu_count

def insert_user_direct(args):
    username, email, password = args
    import mysql.connector
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Aayanali@1208",
        database="test_db"
    )
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO project (username, email, password) VALUES (%s, %s, %s)",
        (username, email, password)
    )
    conn.commit()
    cursor.close()
    conn.close()

def bulk_insert_users(n, num_processes=8):
    start_time = time.time()
    args_list = [
        (f"user{i}", f"user{i}@mail.com", "password")
        for i in range(n)
    ]
    with Pool(processes=num_processes) as pool:
        pool.map(insert_user_direct, args_list)
    end_time = time.time()
    print(f"Inserted {n} users in {end_time - start_time:.2f} seconds using {num_processes} processes.")

if __name__ == "__main__":
    bulk_insert_users(2000, num_processes=8)
