import sqlite3

from fastapi import APIRouter, HTTPException, status
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.schemas import UserLogin, UserRegister
from app.database import get_db_connection
from app.security import create_access_token

ph = PasswordHasher()
router = APIRouter(prefix="/api")

@router.post("/register")
def api_register(user: UserRegister):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))

            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "USER_ALREADY_EXISTS",
                        "message": "Пользователь с такой почтой уже существует."
                    }
                )

            hashed_password = ph.hash(user.password)

            cursor.execute('''INSERT INTO users (email, login, password) VALUES (?, ?, ?)''', 
                           (user.email, user.login, hashed_password))
            
            user_id = cursor.lastrowid

            conn.commit()

            access_token = create_access_token(
                data={"sub": user.email, "user_id": user_id, "name": user.login}
            )

            return {
                "success": True,
                "message": "Успешная регистрация.",
                "data": {
                    "token": access_token,
                    "token_type": "bearer",
                    "user": {
                        "id": user_id,
                        "name": user.login,
                        "email": user.email
                    }
                }
            }
    
    except sqlite3.Error as e:
        return {"error": str(e)}
        
@router.post("/login")
def api_login(user: UserLogin):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id, login, email, password FROM users WHERE email = ?", (user.email,))

            user_data = cursor.fetchone()

            if not user_data:
                raise HTTPException(
                    status = status.HTTP_401_UNAUTHORIZED,
                    detail = {
                        "error": "USER_NOT_FOUND",
                        "message": "Пользователь с такой почтой не найден."
                        }
                )
            
            user_id, login, email, hashed_password = user_data

            try:
                ph.verify(hashed_password, user.password)
                
                access_token = create_access_token(
                    data={"sub": email, "user_id": user_id, "name": login}
                )

                return {
                    "success": True,
                    "message": "Успешный вход.",
                    "data": {
                        "token": access_token,
                        "token_type": "bearer",
                        "user": {
                            "id": user_id,
                            "name": login,
                            "email": email
                        }
                    }
                }
                
            except VerifyMismatchError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error":"INVALID_PASSWORD",
                        "message":"Неверный логин или пароль."
                        }
                )

    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "DATABASE_ERROR",
                "message": "Ошибка базы данных при входе."
            }
        )