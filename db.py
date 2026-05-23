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
    conn = get_connection()
    cursor = conn.cursor()
    query= "SELECT food_id, name, cost, preparingTime, cookingTime, preference FROM foods"
    cursor.execute(query)
    foods = cursor.fetchall()
    cursor.close()
    conn.close()
    return {row[0]: {"name": row[1], "cost": row[2], "preparingTime": row[3],"cookingTime": row[4], "preference": row[5]} for row in foods}  

def get_nutrients():
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT nutrient_id, name, unit FROM nutrients"
    cursor.execute(query)
    nutrients = cursor.fetchall()
    cursor.close()
    conn.close()
    return {row[0]: {"name": row[1], "unit": row[2]} for row in nutrients}

def get_food_nutrients():
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT food_id, nutrient_id, amount FROM food_nutrients"
    cursor.execute(query)
    food_nutrients = cursor.fetchall()
    result = {}
    for food_id, nutrient_id, amount in food_nutrients:
        if food_id not in result:
            result[food_id] = {}
        result[food_id][nutrient_id] = amount
    cursor.close()
    conn.close()
    return result

def get_dri(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT nutrient_id, RLL, RUL, name FROM dri WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    dri = cursor.fetchall()
    cursor.close()
    conn.close()
    return {row[0]: {"RLL": row[1], "RUL": row[2], "name": row[3]} for row in dri}

def get_user_preferences(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT food_id, preference_score FROM user_preferences WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    preferences = cursor.fetchall()
    cursor.close()
    conn.close()
    return {row[0]: row[1] for row in preferences}


food_list = get_foods()
nutrient_list = get_nutrients()
food_nutrient_list = get_food_nutrients()