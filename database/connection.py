from mysql.connector import pooling

pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=16,
    pool_reset_session=True,
    host="localhost",
    user="root",
    password="Aayanali@1208",
    database="test_db"
)

def get_connection():
    return pool.get_connection()

'''
-Sets up the connection pool to MySQL
-Reusable DB connection manager
'''