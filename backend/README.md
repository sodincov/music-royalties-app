docker compose up -d

 2. Остановка проекта (без удаления данных)
docker compose down

4. Полная очистка (остановка + удаление томов = потеря данных!)
docker compose down -v


# Посмотреть запущенные контейнеры
docker ps

# Посмотреть логи БД
docker logs fastapi_db

# Посмотреть логи pgAdmin
docker logs fastapi_pgadmin

# Зайти внутрь контейнера с БД (для отладки)
docker exec -it fastapi_db psql -U fastuser -d fastapi_app

# Запусти сервер с перезагрузкой при изменениях
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Документация (Swagger):
http://127.0.0.1:8000/docs

# Докмуентация (pgAdmin)
http://localhost:5050