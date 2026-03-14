# Comments Service API

Сервис комментариев к постам

## Установка

До начала работы
```bash
pip install -r requirements.txt
```

Docker
```bash
docker compose up --build
```

Для запуска команд на докер-образе требуется использовать
```bash
docker compose exec web python manage.py 'текст команды'

# например:
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Команды внутри образа
```bash
docker compose up -d db
docker compose up -d web
docker compose exec web python manage.py migrate
```

Если нужно сбросить и заново поднять данные БД:
```bash
docker compose down -v
docker compose up --build -d
docker compose exec web python manage.py migrate
```

## Подключение
- Сваггер: `http://localhost:8000/api/docs/`
- Админка: `http://localhost:8000/admin/`

## API Endpoints

### Пользователи
- `GET /api/users/` - Список всех пользователей
- `GET /api/users/{id}/` - Получить пользователя
- `POST /api/users/` - Создать пользователя
- `PUT /api/users/{id}/` - Обновить пользователя
- `DELETE /api/users/{id}/` - Удалить пользователя

### Посты
- `GET /api/posts/` - Список всех постов
- `GET /api/posts/{id}/` - Получить пост
- `POST /api/posts/` - Создать пост
- `PUT /api/posts/{id}/` - Обновить пост
- `DELETE /api/posts/{id}/` - Удалить пост
- `POST /api/posts/{id}/like/` - Добавить/убрать лайк
- `GET /api/posts/{id}/likes/` - Получить количество лайков
- `GET /api/posts/top_by_likes/` - топ-10 постов по лайкам (агрегированные данные)

### Комментарии
- `GET /api/comments/` - Список всех комментариев
- `GET /api/comments/{id}/` - Получить комментарий
- `POST /api/comments/` - Создать комментарий
- `PUT /api/comments/{id}/` - Обновить комментарий
- `DELETE /api/comments/{id}/` - Удалить комментарий
- `POST /api/comments/{id}/like/` - Добавить/убрать лайк
- `GET /api/comments/{id}/likes/` - Получить количество лайков
- `GET /api/comments/top_by_likes/` - топ-10 комментариев по лайкам (агрегированные данные)
