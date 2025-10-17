from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException, status

from app.repositories.user_repository import UserRepository
from app.security import create_access_token

ph = PasswordHasher()

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def register_user(self, email: str, login: str, password: str):
        """Зарегистрировать нового пользователя"""

        if self.user_repository.check_email_exists(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "USER_ALREADY_EXISTS",
                    "message": "Пользователь с такой почтой уже существует."
                }
            )
        
        hashed_password = ph.hash(password)
        
        user_id = self.user_repository.create_user(email, login, hashed_password)
        
        access_token = create_access_token(
            data={"sub": email, "user_id": user_id, "name": login}
        )
        
        return {
            "token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "name": login,
                "email": email
            }
        }
    
    def authenticate_user(self, email: str, password: str):
        """Аутентифицировать пользователя"""

        user_data = self.user_repository.get_user_by_email(email)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "USER_NOT_FOUND",
                    "message": "Пользователь с такой почтой не найден."
                }
            )
        
        user_id, login, email, hashed_password = user_data
        
        try:
            ph.verify(hashed_password, password)
            
            access_token = create_access_token(
                data={"sub": email, "user_id": user_id, "name": login}
            )
            
            return {
                "token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user_id,
                    "name": login,
                    "email": email
                }
            }
            
        except VerifyMismatchError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_PASSWORD",
                    "message": "Неверный логин или пароль."
                }
            )