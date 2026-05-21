import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="",
        password="",
        database=""
    )

conn = get_connection()
if conn.is_connected():
    print("Veritabanına bağlanıldı.")
else:
    print("Veritabanına bağlanılamadı.")

def get_foods():
    pass

def get_nutrients():
    pass

def get_dri():
    pass

def get_user_preferences():
    pass