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

def get_dri(user_id):
    pass

def get_user_preferences(user_id):
    pass

food_list = get_foods()
nutrient_list = get_nutrients()