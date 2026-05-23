import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="heuristic",
        database="diet_menu_optimizer"
    )

def test_connection():
    try:
        conn = get_connection()
        if conn.is_connected():
            print("Connected to the database.")
            conn.close()
        else:
            print("Failed to connect to the database.")
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")

test_connection()

def get_foods():
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT id, name, cost, preparingTime, cookingTime, preference, co2 FROM foods"
    cursor.execute(query)
    foods = cursor.fetchall()
    cursor.close()
    conn.close()
    return {row[0]: {"name": row[1], "cost": row[2], "preparingTime": row[3],
                     "cookingTime": row[4], "preference": row[5], "co2": row[6]} for row in foods}

def get_nutrients():
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT id, name FROM nutrients"
    cursor.execute(query)
    nutrients = cursor.fetchall()
    cursor.close()
    conn.close()
    return {row[0]: {"name": row[1]} for row in nutrients}

def get_food_nutrients():
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT foodId, nutrientId, quantity FROM food_nutrients"
    cursor.execute(query)
    food_nutrients = cursor.fetchall()
    result = {}
    for food_id, nutrient_id, quantity in food_nutrients:
        if food_id not in result:
            result[food_id] = {}
        result[food_id][nutrient_id] = quantity
    cursor.close()
    conn.close()
    return result

def get_dri(user_id):
    # dri tablosunda user_id yok, yaş ve cinsiyete göre filtreleniyor
    conn = get_connection()
    cursor = conn.cursor()
    # Önce kullanıcı bilgilerini al
    cursor.execute("SELECT age, gender FROM user WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        return {}
    age, gender = user
    query = """
        SELECT nutrient_id, RLL, RUL 
        FROM dri 
        WHERE low_age <= %s AND up_age >= %s AND gender = %s
    """
    cursor.execute(query, (age, age, gender))
    dri = cursor.fetchall()
    cursor.close()
    conn.close()
    return {row[0]: {"RLL": row[1], "RUL": row[2]} for row in dri}

def get_user_preferences(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT foodId, preference FROM user_foods WHERE userId = %s"
    cursor.execute(query, (user_id,))
    preferences = cursor.fetchall()
    cursor.close()
    conn.close()
    return {row[0]: row[1] for row in preferences}

food_list = get_foods()
nutrient_list = get_nutrients()
food_nutrient_list = get_food_nutrients()