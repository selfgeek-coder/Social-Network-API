import sqlite3
from fastapi import APIRouter, HTTPException, status, Depends, Query

from app.database import get_db_connection
from app.security import verify_token
from app.schemas import PostCreate, PostDelete, PostEdit

router = APIRouter(prefix="/api/post")

@router.post("/create")
def create_post(post: PostCreate, current_user: dict = Depends(verify_token)):
    """Создает пост"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO posts (title, content, author_id) 
                VALUES (?, ?, ?)
            ''', (post.title, post.content, current_user["user_id"]))
            
            post_id = cursor.lastrowid
            conn.commit()
            
            return {
                "success": True,
                "message": "Пост успешно создан",
                "data": {
                    "post_id": post_id,
                    "title": post.title,
                    "content": post.content,
                    "author_id": current_user["user_id"]
                }
            }
            
    except sqlite3.Error as e:
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
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT author_id FROM posts WHERE id = ?
            ''', (post.post_id,))
            
            post_data = cursor.fetchone()
            
            if not post_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": "POST_NOT_FOUND",
                        "message": "Пост не найден"
                    }
                )
            
            author_id = post_data[0]
            
            if author_id != current_user["user_id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "FORBIDDEN",
                        "message": "Вы можете редактировать только свои посты"
                    }
                )
            
            cursor.execute('''
                UPDATE posts 
                SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (post.title, post.content, post.post_id))
            
            conn.commit()
            
            return {
                "success": True,
                "message": "Пост успешно обновлен",
                "data": {
                    "post_id": post.post_id,
                    "title": post.title,
                    "content": post.content
                }
            }
            
    except sqlite3.Error as e:
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
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT author_id FROM posts WHERE id = ?
            ''', (post.post_id,))
            
            post_data = cursor.fetchone()
            
            if not post_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": "POST_NOT_FOUND",
                        "message": "Пост не найден"
                    }
                )
            
            author_id = post_data[0]
            
            if author_id != current_user["user_id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "FORBIDDEN",
                        "message": "Вы можете удалять только свои посты"
                    }
                )
            
            cursor.execute('DELETE FROM posts WHERE id = ?', (post.post_id,))
            
            conn.commit()
            
            return {
                "success": True,
                "message": "Пост успешно удален",
                "data": {
                    "post_id": post.post_id
                }
            }
            
    except sqlite3.Error as e:
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
    - page: номер страницы (начинается с 1)
    - page_size: количество постов на странице (по умолчанию 10 максимум 50)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            offset = (page - 1) * page_size
            
            cursor.execute('SELECT COUNT(*) FROM posts')
            total_posts = cursor.fetchone()[0]
            
            total_pages = (total_posts + page_size - 1) // page_size
            
            cursor.execute('''
                SELECT p.id, p.title, p.content, p.created_at, u.login as author_name
                FROM posts p
                JOIN users u ON p.author_id = u.id
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
            ''', (page_size, offset))
            
            posts = cursor.fetchall()
            
            news_list = []
            for post in posts:
                post_id, title, content, created_at, author_name = post
                news_list.append({
                    "id": post_id,
                    "title": title,
                    "content": content,
                    "created_at": created_at,
                    "author_name": author_name
                })
            
            return {
                "success": True,
                "data": {
                    "posts": news_list,
                    "pagination": {
                        "current_page": page,
                        "page_size": page_size,
                        "total_posts": total_posts,
                        "total_pages": total_pages,
                        "has_next": page < total_pages,
                        "has_prev": page > 1
                    }
                }
            }
            
    except sqlite3.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "DATABASE_ERROR",
                "message": "Ошибка базы данных при получении новостей"
            }
        )