# Comments Service API

Сервис комментариев к постам

## Установка

До начала работы
```bash
pip install -r requirements.txt```

Docker
```bash
docker compose up --build
```

Для запуска команд на докер-образе требуется использовать 
```bash
docker compose exec web 'текст команды'
```

Команды внутри образа
```bash
python manage.py migrate
python manage.py createsuperuser
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

### Комментарии
- `GET /api/comments/` - Список всех комментариев
- `GET /api/comments/{id}/` - Получить комментарий
- `POST /api/comments/` - Создать комментарий
- `PUT /api/comments/{id}/` - Обновить комментарий
- `DELETE /api/comments/{id}/` - Удалить комментарий
- `POST /api/comments/{id}/like/` - Добавить/убрать лайк
- `GET /api/comments/{id}/likes/` - Получить количество лайков
