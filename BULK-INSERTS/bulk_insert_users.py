import time

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.user_model import insert_user

def bulk_insert_users(n):
    start_time = time.time()
    for i in range(n):
        username = f"user{i}"
        email = f"user{i}@mail.com"
        password = "password"
        insert_user(username, email, password)
    end_time = time.time()
    print(f"Inserted {n} users in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    bulk_insert_users(500)