from pydantic import BaseModel, EmailStr, field_validator, Field, constr

class UserRegister(BaseModel):
    email: EmailStr
    login: str
    password: str

    @field_validator('login')
    @classmethod
    def validate_login(cls, v):
        if len(v) < 3:
            raise ValueError('Логин должен содержать минимум 3 символа.')
        
        if ' ' in v:
            raise ValueError('Логин не должен содержать пробелы.')
        
        forbidden_chars = '<>"*&|\\/[]{}'
        for char in v:
            if char in forbidden_chars:
                raise ValueError(f'Логин не должен содержать запрещенные символы.')
        
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов.')
        
        return v

class UserLogin(BaseModel):
    email: EmailStr
    login: str
    password: str

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Заголовок поста")
    content: str = Field(..., min_length=1, max_length=10000, description="Содержание поста")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Заголовок не может быть пустым.')
        
        if len(v) < 3:
            raise ValueError('Заголовок должен содержать минимум 3 символа.')
        
        if v[0].islower():
            raise ValueError('Заголовок должен начинаться с заглавной буквы.')
        
        return v

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Содержание не может быть пустым')
        
        if len(v) < 12:
            raise ValueError('Содержание должно быть не менее 12 символов')

        return v

class PostEdit(BaseModel):
    post_id: int
    title: str = Field(..., min_length=1, max_length=200, description="Заголовок поста")
    content: str = Field(..., min_length=1, max_length=10000, description="Содержание поста")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Заголовок не может быть пустым.')
        
        if len(v) < 3:
            raise ValueError('Заголовок должен содержать минимум 3 символа.')
        
        if v[0].islower():
            raise ValueError('Заголовок должен начинаться с заглавной буквы.')
        
        return v

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Содержание не может быть пустым.')
        
        if len(v) < 12:
            raise ValueError('Содержание должно быть не менее 12 символов.')

        return v

class PostDelete(BaseModel):
    post_id: int