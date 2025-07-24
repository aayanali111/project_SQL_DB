import time
from multiprocessing import Pool, cpu_count
from model.user_model import insert_user


def bulk_insert_users(n, num_processes=8):
    start_time = time.time()
    args_list = [
        (f"user{i}", f"user{i}@mail.com", "password")
        for i in range(n)
    ]
    with Pool(processes=num_processes) as pool:
        pool.starmap(insert_user, args_list)
    end_time = time.time()
    print(f"Inserted {n} users in {end_time - start_time:.2f} seconds using {num_processes} processes.")

if __name__ == "__main__":
    bulk_insert_users(2000, num_processes=8)
