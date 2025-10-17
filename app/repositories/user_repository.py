from typing import Optional, Tuple

from app.database import get_db_connection

class UserRepository:
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Tuple]:
        """Получить пользователя по email"""
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, login, email, password FROM users WHERE email = ?", 
                (email,)
            )
            return cursor.fetchone()
    
    @staticmethod
    def create_user(email: str, login: str, hashed_password: str) -> int:
        """Создать нового пользователя"""

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (email, login, password) VALUES (?, ?, ?)",
                (email, login, hashed_password)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
    
    @staticmethod
    def check_email_exists(email: str) -> bool:
        """Проверить существование email"""

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            return cursor.fetchone() is not None