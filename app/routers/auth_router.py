from fastapi import APIRouter, HTTPException, status

from app.schemas import UserLogin, UserRegister
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api", tags=["Auth API"])

# Инициализация зависимостей
user_repository = UserRepository()
auth_service = AuthService(user_repository)

@router.post("/register")
def api_register(user: UserRegister):
    try:
        result = auth_service.register_user(user.email, user.login, user.password)
        
        return {
            "success": True,
            "message": "Успешная регистрация.",
            "data": result
        }
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "REGISTRATION_ERROR",
                "message": "Ошибка при регистрации пользователя"
            }
        )

@router.post("/login")
def api_login(user: UserLogin):
    try:
        result = auth_service.authenticate_user(user.email, user.password)
        
        return {
            "success": True,
            "message": "Успешный вход.",
            "data": result
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "LOGIN_ERROR",
                "message": "Ошибка при входе в систему"
            }
        )