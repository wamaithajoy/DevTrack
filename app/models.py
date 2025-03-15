class User:
    def __init__(self, id: int, username: str, password: str):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get_user_by_username(db, username: str):
        """Retrieve a user from the database by username."""
        cursor = db.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        return User(*result) if result else None

    @staticmethod
    def create_user(db, username: str, hashed_password: str):
        """Insert a new user into the database."""
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        db.commit()
        cursor.close()
