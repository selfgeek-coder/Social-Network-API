from fastapi import APIRouter, HTTPException, status, Depends, Query

from app.schemas import PostCreate, PostDelete, PostEdit
from app.security import verify_token
from app.repositories.post_repository import PostRepository
from app.services.post_service import PostService

router = APIRouter(prefix="/api/post", tags=["CRUD Posts API"])

post_repository = PostRepository()
post_service = PostService(post_repository)

@router.post("/create")
def create_post(post: PostCreate, current_user: dict = Depends(verify_token)):
    """Создает пост"""

    try:
        result = post_service.create_post(
            post.title, post.content, current_user["user_id"]
        )
        
        return {
            "success": True,
            "message": "Пост успешно создан",
            "data": result
        }
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "DATABASE_ERROR",
                "message": "Ошибка базы данных при создании поста"
            }
        )

@router.put("/edit")
def edit_post(post: PostEdit, current_user: dict = Depends(verify_token)):
    """Изменяет пост по ID"""

    try:
        result = post_service.update_post(
            post.post_id, post.title, post.content, current_user["user_id"]
        )
        
        return {
            "success": True,
            "message": "Пост успешно обновлен",
            "data": result
        }
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "DATABASE_ERROR",
                "message": "Ошибка базы данных при редактировании поста"
            }
        )

@router.delete("/delete")
def delete_post(post: PostDelete, current_user: dict = Depends(verify_token)):
    """Удаляет пост по ID"""

    try:
        result = post_service.delete_post(post.post_id, current_user["user_id"])
        
        return {
            "success": True,
            "message": "Пост успешно удален",
            "data": result
        }
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "DATABASE_ERROR",
                "message": "Ошибка базы данных при удалении поста"
            }
        )

@router.get("/news")
@router.get("/news/{page}")
def get_news(page: int = 1, page_size: int = Query(default=10, ge=1, le=50)):
    """
    page: номер страницы (начинается с 1)
    page_size: количество постов на странице (по умолчанию 10 максимум 50)
    """
    
    if page < 1:
        page = 1

    try:
        result = post_service.get_news(page, page_size)
        
        return {
            "success": True,
            "data": result
        }
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "DATABASE_ERROR",
                "message": "Ошибка базы данных при получении новостей"
            }
        )