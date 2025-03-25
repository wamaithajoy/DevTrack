import mysql.connector
import os
from dotenv import load_dotenv

# Loading environment variables from .env file
load_dotenv()

# Retrieve database credentials from .env
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# Function to create a database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        print("✅ Database connection successful!")
        return conn
    except mysql.connector.Error as e:
        print(f"❌ Database connection failed: {e}")
        return None
    

# Function to create the users table
def create_users_table():
    conn = get_db_connection()  # Create a new database connection
    if conn:
        cursor = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Users table created (or already exists).")
    else:
        print("❌ Could not create users table because the database connection failed.")

# Calling the function when the app starts
create_users_table()   



# Function to create tracking table
def create_tracking_table():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tracking (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            project_name VARCHAR(255) NOT NULL,
            commits INT DEFAULT 0,
            api_requests INT DEFAULT 0,
            errors INT DEFAULT 0,
            response_time FLOAT DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Tracking table created (or already exists).")

# Call the function
create_tracking_table()
