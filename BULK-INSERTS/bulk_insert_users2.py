import time

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.user_model import insert_user
from concurrent.futures import ThreadPoolExecutor

def bulk_insert_users(n, max_workers=20):
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i in range(n):
            username = f"user{i}"
            email = f"user{i}@mail.com"
            password = "password"
            futures.append(executor.submit(insert_user, username, email, password))
        for future in futures:
            future.result()
    end_time = time.time()
    print(f"Inserted {n} users in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    bulk_insert_users(500)
