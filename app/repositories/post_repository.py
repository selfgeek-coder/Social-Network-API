from typing import Optional, List, Tuple

from app.database import get_db_connection

class PostRepository:
    @staticmethod
    def create_post(title: str, content: str, author_id: int) -> int:
        """Создать новый пост"""

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)",
                (title, content, author_id)
            )
            post_id = cursor.lastrowid
            conn.commit()
            return post_id
    
    @staticmethod
    def get_post_by_id(post_id: int) -> Optional[Tuple]:
        """Получить пост по post_id: int"""

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, content, author_id FROM posts WHERE id = ?",
                (post_id,)
            )
            return cursor.fetchone()
    
    @staticmethod
    def update_post(post_id: int, title: str, content: str) -> bool:
        """Обновить пост"""

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE posts 
                SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?""",
                (title, content, post_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def delete_post(post_id: int) -> bool:
        """Удалить пост"""

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def get_posts_paginated(page: int, page_size: int) -> Tuple[List[Tuple], int, int]:
        """Получить посты с пагинацией"""

        with get_db_connection() as conn:
            cursor = conn.cursor()
            offset = (page - 1) * page_size

            cursor.execute("SELECT COUNT(*) FROM posts")
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
            return posts, total_posts, total_pages