import json
import secrets
import shutil
from pathlib import Path
from uuid import uuid4
from fastapi import Depends
from fastapi import FastAPI, UploadFile, Form, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
# ============================================================
# ПУТИ
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / "users.json"
FILES_DIR = BASE_DIR / "files"
FILES_DIR.mkdir(
    parents=True,
    exist_ok=True
)
# ============================================================
# FASTAPI
# ============================================================
app = FastAPI()
templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)
# ============================================================
# СЕССИИ
# token -> login
#
# После перезапуска сервера все токены сбрасываются.
# ============================================================
sessions = {}
# ============================================================
# USERS.JSON
# ============================================================
def load_users():
    if not USERS_FILE.exists():
        return []
    try:
        with open(
            USERS_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

def save_users(users):
    # Сначала пишем временный файл.
    # Это уменьшает вероятность получить битый users.json,
    # если процесс будет прерван во время записи.
    temp_file = USERS_FILE.with_suffix(".tmp")
    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            users,
            f,
            ensure_ascii=False,
            indent=4
        )
    temp_file.replace(USERS_FILE)

def get_user(login):
    users = load_users()
    for user in users:
        if user.get("login") == login:
            return user
    return None
# ============================================================
# АВТОРИЗАЦИЯ
# ============================================================
def get_user_by_token(token):
    if not token:
        return None
    login = sessions.get(token)
    if not login:
        return None
    return get_user(login)

def get_current_user(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Необходима авторизация"
        )
    if token.startswith("Bearer "):
        token = token[7:]
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Сессия недействительна"
        )
    return user
# ============================================================
# ПАПКА ПОЛЬЗОВАТЕЛЯ
# ============================================================

def get_user_directory(user):

    relative_directory = user.get(
        "filedirectory"
    )
    if not relative_directory:
        raise HTTPException(
            status_code=500,
            detail="У пользователя отсутствует директория"
        )
    user_dir = (
        BASE_DIR / relative_directory
    ).resolve()
    # Дополнительная защита:
    # папка пользователя обязана находиться внутри FILES_DIR.
    files_root = FILES_DIR.resolve()
    try:
        user_dir.relative_to(files_root)
    except ValueError:
        raise HTTPException(
            status_code=500,
            detail="Некорректная директория пользователя"
        )
    user_dir.mkdir(
        parents=True,
        exist_ok=True
    )
    return user_dir
# ============================================================
# МОДЕЛИ
# ============================================================

class LoginData(BaseModel):
    login: str
    password: str


class RegisterData(BaseModel):
    login: str
    password: str

# ============================================================
# ГЛАВНАЯ СТРАНИЦА
# ============================================================

@app.get("/",response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request
        }
    )

# ============================================================
# РЕГИСТРАЦИЯ
# ============================================================
@app.post("/register/")
def register(data: RegisterData):
    login = data.login.strip()
    password = data.password
    if not login:
        raise HTTPException(
            status_code=400,
            detail="Введите логин"
        )

    if not password:
        raise HTTPException(
            status_code=400,
            detail="Введите пароль"
        )

    if len(login) < 3:
        raise HTTPException(
            status_code=400,
            detail="Логин должен содержать минимум 3 символа"
        )

    if len(login) > 32:
        raise HTTPException(
            status_code=400,
            detail="Логин слишком длинный"
        )

    if len(password) < 4:
        raise HTTPException(
            status_code=400,
            detail="Пароль должен содержать минимум 4 символа"
        )

    # --------------------------------------------------------
    # Разрешаем только простой набор символов в логине.
    # --------------------------------------------------------

    if not all(
        c.isalnum() or c in "_-"
        for c in login
    ):
        raise HTTPException(
            status_code=400,
            detail="Логин может содержать буквы, цифры, _ и -"
        )

    # --------------------------------------------------------
    # Проверяем существующий логин
    # --------------------------------------------------------
    users = load_users()
    login_lower = login.lower()
    for user in users:
        if user.get("login", "").lower() == login_lower:
            raise HTTPException(
                status_code=400,
                detail="Такой логин уже существует"
            )

    # --------------------------------------------------------
    # Создаём уникальную директорию
    # --------------------------------------------------------

    user_uuid = str(uuid4())

    relative_directory = (
        "files/" + user_uuid
    )

    user_directory = (
        BASE_DIR / relative_directory
    )

    user_directory.mkdir(
        parents=True,
        exist_ok=False
    )

    # --------------------------------------------------------
    # Создаём пользователя
    # --------------------------------------------------------

    user = {
        "login": login,
        "password": password,
        "filedirectory": relative_directory
    }

    users.append(user)

    save_users(users)

    # --------------------------------------------------------
    # Сразу создаём авторизацию
    # --------------------------------------------------------

    token = secrets.token_urlsafe(32)

    sessions[token] = login

    return {
        "success": True,
        "token": token,
        "login": login
    }


# ============================================================
# LOGIN
# ============================================================

@app.post("/login/")
def login(data: LoginData):

    login_value = data.login.strip()
    password = data.password

    user = get_user(login_value)

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль"
        )

    if user.get("password") != password:

        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль"
        )

    # Новый случайный token

    token = secrets.token_urlsafe(32)

    sessions[token] = user["login"]

    return {
        "success": True,
        "token": token,
        "login": user["login"]
    }


# ============================================================
# LOGOUT
# ============================================================

@app.post("/logout/")
def logout(request: Request):
    token = request.headers.get(
        "Authorization"
    )
    if token and token.startswith("Bearer "):
        token = token[7:]
    if token:
        sessions.pop(
            token,
            None
        )
    return {
        "success": True
    }
# ============================================================
# ТЕКУЩИЙ ПОЛЬЗОВАТЕЛЬ
# ============================================================

@app.get("/me/")
def me(request: Request):
    user = get_current_user(request)
    return {
        "login": user["login"]
    }

# ============================================================
# СТРАНИЦА ФАЙЛОВ
# ============================================================

@app.get("/files_client.html",response_class=HTMLResponse)
async def files_page(request: Request):
    return templates.TemplateResponse(
        "files_client.html",
        {
            "request": request
        }
    )


# ============================================================
# СПИСОК ФАЙЛОВ
# ============================================================

@app.get("/files/")
def list_files(request: Request):
    user = get_current_user(request)
    user_dir = get_user_directory(user)
    files = []
    for path in user_dir.iterdir():
        if path.is_file():
            files.append(
                path.name
            )
    files.sort(
        key=str.lower
    )

    return {
        "files": files
    }

# ============================================================
# DOWNLOAD
# ============================================================

@app.get("/download/{filename:path}")
def download_file(filename: str,request: Request):
    user = get_current_user(request)
    user_dir = get_user_directory(user)
    # Берём только путь внутри папки пользователя.
    file_path = (
        user_dir / filename
    ).resolve()
    try:

        file_path.relative_to(
            user_dir.resolve()
        )
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Доступ запрещён"
        )
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Файл не найден"
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Файл не найден"
        )
    return FileResponse(
        str(file_path),
        filename=file_path.name
    )

@app.delete("/delete/{filename:path}")
def delete_file(filename: str, user: dict = Depends(get_current_user)):
    user_dir = get_user_directory(user)

    # Защита от выхода из папки пользователя
    file_path = (user_dir / filename).resolve()

    if user_dir.resolve() not in file_path.parents:
        raise HTTPException(status_code=403, detail="Access denied")

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    file_path.unlink()

    return {"ok": True}

# ============================================================
# UPLOAD CHUNK
# ============================================================

@app.post("/upload_chunk/")
async def upload_chunk(
    request: Request,
    file: UploadFile,
    filename: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...)
):

    user = get_current_user(request)

    user_dir = get_user_directory(user)

    # --------------------------------------------------------
    # Проверяем параметры
    # --------------------------------------------------------
    if chunk_index < 0:
        raise HTTPException(
            status_code=400,
            detail="Некорректный chunk_index"
        )
    if total_chunks <= 0:
        raise HTTPException(
            status_code=400,
            detail="Некорректное количество chunks"
        )
    if chunk_index >= total_chunks:
        raise HTTPException(
            status_code=400,
            detail="Некорректный chunk_index"
        )

    # --------------------------------------------------------
    # Только имя файла, без ../
    # --------------------------------------------------------

    filename = Path(filename).name

    if not filename:

        raise HTTPException(
            status_code=400,
            detail="Некорректное имя файла"
        )
    # --------------------------------------------------------
    # Временная папка
    # --------------------------------------------------------
    temp_dir = (
        user_dir /
        (filename + "_tmp")
    )
    temp_dir.mkdir(
        parents=True,
        exist_ok=True
    )
    chunk_path = (
        temp_dir /
        f"{chunk_index}.part"
    )
    # --------------------------------------------------------
    # Записываем chunk
    # --------------------------------------------------------
    with open(
        chunk_path,
        "wb"
    ) as f:
        while True:
            data = await file.read(
                1024 * 1024
            )
            if not data:
                break
            f.write(data)
    # --------------------------------------------------------
    # Проверяем наличие ВСЕХ chunks
    #
    # Теперь последний chunk не обязан прийти последним.
    # --------------------------------------------------------
    all_chunks = True
    for i in range(total_chunks):
        part_path = (
            temp_dir /
            f"{i}.part"
        )
        if not part_path.exists():
            all_chunks = False
            break
    # --------------------------------------------------------
    # Склеиваем
    # --------------------------------------------------------
    if all_chunks:
        final_path = (
            user_dir /
            filename
        )
        # Сначала собираем во временный итоговый файл.
        # Это лучше, чем сразу портить существующий файл.
        assembling_path = (
            user_dir /
            (filename + ".assembling")
        )
        try:
            with open(
                assembling_path,
                "wb"
            ) as final_file:
                for i in range(total_chunks):
                    part_path = (
                        temp_dir /
                        f"{i}.part"
                    )
                    with open(
                        part_path,
                        "rb"
                    ) as part_file:
                        shutil.copyfileobj(
                            part_file,
                            final_file,
                            length=1024 * 1024
                        )
            # После успешной сборки заменяем файл.
            assembling_path.replace(
                final_path
            )

            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )
        except Exception:
            if assembling_path.exists():
                assembling_path.unlink()
            raise
    return {
        "chunk_index": chunk_index,
        "complete": all_chunks
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
