# Проект Фудграм
Фудграм — проект, цель которого дать возможность пользователям создавать и хранить рецепты на онлайн-платформе. Кроме того, можно скачать список продуктов, необходимых для приготовления блюда, просмотреть рецепты друзей и добавить любимые рецепты в список избранных.

## Технологии

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

## Настройка
### Репозиторий

Проект имеет следующую структуру:
- `backend` - папка для кода Backend приложения (Django)
- `docs` - папка со спецификациями API
- `frontend` - папка для кода Frontend приложения
- `infra` - папка для настроек приложений и файлов развертывания инфраструктуры для локальной отладки, а также с конфигурациями nginx
- `postman_collection` - папка с коллекцией postman
- `docker-compose.production.yml` - настройки для развёртывания приложения

### Настройка после клонирования репозитория


После клонирования репозитория устанавливаем и настраиваем виртуальное окружение:

<details>
<summary>
Виртуальное окружение для backend
</summary>

1. Переходим в папку `/backend/foodgram_backend`
2. Устанавливаем и активируем виртуальное окружение
    - Для linux/mac:
      ```shell
      python3.11 -m venv venv
      source .venv/bin/activate
      ```
    - Для Windows:
      ```shell
      python -m venv venv
      source venv\Scripts\activate
      ```
    В начале командной строки должно появиться название виртуальног окружения `(venv)`
3. Устанавливаем зависимости
    ```shell
    pip install -r requirements.txt
    ```
</details>

## Запуск приложения локально.


1. Создать `.env` на основе указанного ниже примера. Указав валидные данные для подключения.

      ```ini
      SECRET_KEY=django-secret-key
      DEBUG=True
      POSTGRES_USER=foodgram_user
      POSTGRES_PASSWORD=foodgram_password
      POSTGRES_DB=foodgram
      DB_HOST=db
      DB_PORT=5432
      ALLOWED_HOSTS=example.com 127.0.0.1 localhost
      TRUST_URL=https://example.com

      ```
2. Создать файл `docker-compose.yml` (скопируйте всё из файла `docker-compose.production.yml`, поменяйте поля image на `build: ./{соответствующая папка}/`)
3. В настройках Django приложения `setting.py` в качестве базы данных стоит PostgreSQL. При необходмости изменить на SQLite, закоментировать настройки для БД на основе PostgreSQL и раскоментировать настройки для SQLite. А также закоментировать в `/foodgram/docker-compose.yml` контейнер с db.
4. При необходимости, поменять порт в Dockerfile'ах и конфигурации nginx.
5. Находясь в папке `foodgram` выполните команду `docker compose up`.
6. По адресу http://localhost:8000 будет доступен проект
7. Находясь в папке `infra` выполните команду `docker compose up`.
8. По адресу http://localhost:8000/api/docs/ вы увидите спецификацию API с примерами запросов и спецификацией проекта.

