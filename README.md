# TaskPilot - Менеджер задач с OAuth авторизацией

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.2-blue)
![Redis](https://img.shields.io/badge/Redis-7.2.4-red)

**TaskPilot** - это современное веб-приложение для управления задачами (Todo List), построенное на FastAPI с поддержкой OAuth2 авторизации через Google, Yandex и VK.

## Содержание

- [Возможности](#возможности)
- [Технологии](#технологии)
- [Архитектура проекта](#архитектура-проекта)
- [Установка и запуск](#установка-и-запуск)
- [Запуск с Docker](#запуск-с-docker)
- [Конфигурация](#конфигурация)
- [API Документация](#api-документация)
- [Структура проекта](#структура-проекта)
- [Тестирование](#тестирование)
- [Использование Makefile](#использование-makefile)
- [Миграции базы данных](#миграции-базы-данных)
- [OAuth настройка](#oauth-настройка)
- [Примеры использования](#примеры-использования)
- [Разработка](#разработка)

## Возможности

**Многофакторная аутентификация**

- Регистрация и вход по email/паролю
- OAuth2 авторизация через Google, Yandex, VK
- JWT токены для защищенных endpoint'ов
- Безопасное хеширование паролей (bcrypt)

**Управление задачами**

- Создание, редактирование и удаление задач
- Категоризация задач (работа, личное, учёба, покупки, здоровье, финансы)
- Установка сроков выполнения
- Отметка выполненных задач
- Личный список задач для каждого пользователя

**Администрирование**

- Роли пользователей (пользователь/администратор)
- Административная панель для управления всеми задачами
- Управление пользователями

**Email уведомления**

- Асинхронная отправка email через Gmail SMTP
- Подтверждение регистрации (опционально)

**База данных и кеширование**

- PostgreSQL для хранения данных
- Redis для кеширования OAuth состояний
- Alembic для миграций БД

## Технологии

### Backend

- **FastAPI** - современный асинхронный веб-фреймворк
- **SQLAlchemy 2.0** - ORM для работы с базой данных
- **Alembic** - инструмент для миграций БД
- **Pydantic** - валидация данных и настроек
- **Python-JOSE** - работа с JWT токенами
- **Passlib + Bcrypt** - хеширование паролей

### База данных

- **PostgreSQL 16.2** - основная СУБД
- **Redis 7.2.4** - кеширование и сессии

### Инфраструктура

- **Docker & Docker Compose** - контейнеризация
- **Poetry** - управление зависимостями
- **Uvicorn** - ASGI сервер

## Архитектура проекта

Проект следует **слоистой архитектуре** с разделением ответственности:

```
app/
├── auth/              # Модуль аутентификации
│   ├── client/        # OAuth клиенты (Google, VK, Yandex)
│   ├── jwt.py         # Работа с JWT токенами
│   └── auth_service.py # Бизнес-логика аутентификации
├── database/          # Слой работы с БД
│   ├── models/        # SQLAlchemy модели
│   ├── database.py    # Подключение к БД
│   └── dependencies.py # Dependency Injection
├── handlers/          # API endpoint'ы (контроллеры)
├── repositories/      # Репозитории для работы с моделями
├── schema/            # Pydantic схемы (DTO)
├── service/           # Бизнес-логика
└── migrations/        # Alembic миграции
```

### Слои приложения:

1. **Handlers** (Presentation) - HTTP обработчики, валидация входных данных
2. **Services** (Business Logic) - бизнес-логика приложения
3. **Repositories** (Data Access) - абстракция работы с БД
4. **Models** (Domain) - модели данных

## Установка и запуск

### Предварительные требования

- Python 3.12+
- Poetry
- Docker и Docker Compose
- PostgreSQL (опционально, можно использовать Docker)
- Redis (опционально, можно использовать Docker)

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd TaskPilot
```

### 2. Установка зависимостей

```bash
# Установка Poetry (если не установлен)
curl -sSL https://install.python-poetry.org | python3 -

# Установка зависимостей проекта
poetry install
```

### 3. Настройка окружения

Скопируйте файл с примером и заполните своими данными:

```bash
cp .env.example .env
```

Отредактируйте `.env` файл, заполнив все необходимые переменные (см. [Конфигурация](#конфигурация)).

### 4. Запуск инфраструктуры (Docker)

```bash
# Запуск PostgreSQL и Redis
make docker-u
# или
docker-compose up -d
```

### 5. Применение миграций

```bash
# Применить все миграции
make mig-up
# или
alembic upgrade head
```

### 6. Запуск приложения

```bash
# Запуск через Makefile
make run

# Или напрямую через poetry
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Приложение будет доступно по адресу: http://127.0.0.1:8000

## Запуск с Docker

### Полный запуск всех сервисов

Проект полностью dockerизирован. Вы можете запустить все сервисы (приложение, PostgreSQL, Redis) одной командой:

```bash
# Сборка и запуск всех контейнеров
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

Приложение будет доступно по адресу: http://localhost:8000

### Управление контейнерами

```bash
# Остановить все контейнеры
docker-compose down

# Остановить и удалить все данные (volumes)
docker-compose down -v

# Просмотр логов
docker-compose logs -f app

# Перезапуск сервиса приложения
docker-compose restart app
```

### Применение миграций в Docker

```bash
# Выполнить миграции в контейнере
docker-compose exec app alembic upgrade head

# Создать новую миграцию
docker-compose exec app alembic revision --autogenerate -m "название миграции"
```

### Структура Docker

Проект использует три контейнера:

- **app** - FastAPI приложение (порт 8000)
- **postgres** - PostgreSQL база данных (порт 5432)
- **cacher** - Redis для кеширования (порт 6379)

Все сервисы настроены на автоматический перезапуск и изоляцию в отдельной сети.

## Конфигурация

Все настройки приложения находятся в файле `.env`. Создайте его на основе `.env.example`:

### Основные настройки

```env
APP_NAME=Task Pilot
APP_VERSION=1.0.0
API_VERSION_PREFIX=/api/v1
```

### База данных PostgreSQL

```env
DATABASE_URL=postgresql+asyncpg://admin:admin1234@localhost:5432/db_task_pilot
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin1234
POSTGRES_DB=db_task_pilot
```

### Redis

```env
REDIS_URL=redis://localhost:6379
```

### JWT токены

```env
# Сгенерируйте надежный ключ: openssl rand -hex 32
JWT_SECRET_KEY=your_super_secret_key_change_me
JWT_ALGORITHM=HS256
```

### Email (Gmail)

```env
GMAIL_SMTP_HOST=smtp.gmail.com
GMAIL_SMTP_PORT=587
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
```

Для получения App Password:

1. Перейдите в настройки Google аккаунта
2. Безопасность → Двухфакторная аутентификация
3. App Passwords → Создайте пароль для приложения

### OAuth настройка (см. [OAuth настройка](#-oauth-настройка))

## API Документация

После запуска приложения документация доступна по адресам:

- **Swagger UI**: http://127.0.0.1:8000/api/v1/docs
- **ReDoc**: http://127.0.0.1:8000/api/v1/redoc
- **OpenAPI Schema**: http://127.0.0.1:8000/api/v1/openapi.json

### Основные эндпоинты

#### Аутентификация

- `POST /api/v1/auth/register` - Регистрация пользователя
- `POST /api/v1/auth/login` - Вход (получение JWT токена)
- `GET /api/v1/auth/login/{provider}` - OAuth авторизация (google/yandex/vk)
- `GET /api/v1/auth/me` - Получение информации о текущем пользователе

#### Задачи

- `GET /api/v1/todo_items/all` - Получить все задачи текущего пользователя
- `POST /api/v1/todo_items/` - Создать новую задачу
- `GET /api/v1/todo_items/{id}` - Получить задачу по ID
- `PATCH /api/v1/todo_items/{id}` - Обновить задачу
- `DELETE /api/v1/todo_items/{id}` - Удалить задачу

#### Администрирование (только для админов)

- `GET /api/v1/admin/todo_items/all` - Получить все задачи всех пользователей
- `DELETE /api/v1/admin/todo_items/{id}` - Удалить любую задачу

#### Пользователи

- `GET /api/v1/users/all` - Получить всех пользователей
- `GET /api/v1/users/{id}` - Получить пользователя по ID

## Структура проекта

```
TaskPilot/
├── app/
│   ├── auth/                    # Модуль аутентификации
│   │   ├── client/              # OAuth2 клиенты
│   │   │   ├── google.py        # Google OAuth
│   │   │   ├── yandex.py        # Yandex OAuth
│   │   │   └── vk.py            # VK OAuth
│   │   ├── auth_dependencies.py # Зависимости для авторизации
│   │   ├── auth_handlers.py     # API эндпоинты авторизации
│   │   ├── auth_service.py      # Сервис аутентификации
│   │   └── jwt.py               # Работа с JWT токенами
│   ├── database/                # Работа с базой данных
│   │   ├── models/              # SQLAlchemy модели
│   │   │   ├── enums.py         # Enum типы
│   │   │   ├── todo_category.py # Модель категорий
│   │   │   ├── todo_item.py     # Модель задач
│   │   │   └── user.py          # Модель пользователей
│   │   ├── database.py          # Настройка подключения
│   │   ├── dependencies.py      # DI контейнер
│   │   └── session.py           # Управление сессиями
│   ├── handlers/                # API обработчики (роутеры)
│   │   ├── admin_todo_items.py  # Админ эндпоинты
│   │   ├── todo_item.py         # Эндпоинты задач
│   │   └── user.py              # Эндпоинты пользователей
│   ├── migrations/              # Alembic миграции
│   │   ├── versions/            # Файлы миграций
│   │   └── env.py               # Конфигурация Alembic
│   ├── repositories/            # Репозитории (Data Access Layer)
│   │   ├── todo_item.py         # Репозиторий задач
│   │   └── user.py              # Репозиторий пользователей
│   ├── schema/                  # Pydantic схемы (DTO)
│   │   ├── todo_item.py         # Схемы задач
│   │   └── user.py              # Схемы пользователей
│   ├── service/                 # Бизнес-логика
│   │   ├── email.py             # Email сервис
│   │   ├── todo_item.py         # Сервис задач
│   │   └── user.py              # Сервис пользователей
│   ├── main.py                  # Точка входа приложения
│   └── settings.py              # Настройки приложения
├── tests/                       # Тесты
│   ├── conftest.py              # Конфигурация pytest
│   ├── test_auth.py             # Тесты аутентификации
│   ├── test_todo_items.py       # Тесты CRUD задач
│   ├── test_users.py            # Тесты пользователей
│   ├── test_admin.py            # Тесты админки
│   ├── test_utils.py            # Вспомогательные функции
│   └── README.md                # Документация тестов
├── .coveragerc                  # Конфигурация coverage
├── .dockerignore                # Docker исключения
├── .env.example                 # Пример конфигурации
├── .gitignore                   # Git исключения
├── alembic.ini                  # Конфигурация Alembic
├── docker-compose.yml           # Оркестрация контейнеров (app, postgres, redis)
├── Dockerfile                   # Образ приложения
├── Makefile                     # Makefile с командами
├── pytest.ini                   # Конфигурация pytest
├── pyproject.toml               # Зависимости и метаданные
└── README.md                    # Документация проекта
```

## Тестирование

Проект включает полный набор автоматических тестов, покрывающих все основные функции.

### Запуск тестов

```bash
# Запустить все тесты
make test

# Запустить с подробным выводом
make test-v

# Запустить с отчетом о покрытии кода
make test-cov

# Запустить конкретный тест
make test-one TEST=tests/test_auth.py
```

### Покрытие тестов

- **Аутентификация** - регистрация, вход, JWT токены
- **CRUD задач** - создание, чтение, обновление, удаление
- **Пользователи** - профили, списки, безопасность
- **Администрирование** - доступ, операции, защита

Подробнее см. [tests/README.md](tests/README.md)

### Требования для тестов

1. Создайте тестовую БД:

```bash
psql -U postgres -c "CREATE DATABASE test_taskpilot;"
```

2. Убедитесь что PostgreSQL и Redis запущены:

```bash
make docker-u
```

## Использование Makefile

Проект включает Makefile с удобными командами:

```bash
# Показать все доступные команды
make help

# Запуск приложения
make run

# Остановить процесс на порту 8000
make k-port

# Работа с зависимостями
make list                   # Показать установленные пакеты
make add LIB=fastapi        # Добавить пакет
make add-dev LIB=pytest     # Добавить dev-пакет
make del LIB=fastapi        # Удалить пакет

# Форматирование кода
make format                 # Форматирование с isort

# Очистка
make clean                  # Удалить __pycache__

# Тестирование
make test                   # Запустить все тесты
make test-v                 # Запустить с подробным выводом
make test-cov               # Запустить с покрытием кода
make test-one TEST=path     # Запустить конкретный тест

# Миграции
make mig M="описание"       # Создать новую миграцию
make mig-up                 # Применить миграции

# Docker
make docker-u               # Запустить контейнеры
make docker-d               # Остановить контейнеры
```

## Миграции базы данных

### Первый запуск проекта

Если вы впервые разворачиваете проект, рекомендуется создать миграции с чистого листа:

```bash
# 1. Удалите старые миграции (если есть)
rm app/migrations/versions/*.py

# 2. Создайте начальную миграцию
make mig M="Initial migration"
# или
alembic revision --autogenerate -m "Initial migration"

# 3. Примените миграцию
make mig-up
```

**Примечание**: Миграции должны быть в Git, так как они являются частью проекта и обеспечивают историю изменений схемы базы данных.

### Создание новой миграции

```bash
# Через Makefile
make mig M="Добавлена таблица tasks"

# Или напрямую
alembic revision --autogenerate -m "Добавлена таблица tasks"
```

### Применение миграций

```bash
# Применить все миграции
make mig-up
# или
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# Откатить все миграции
alembic downgrade base
```

### История миграций

```bash
# Посмотреть текущую версию
alembic current

# Посмотреть историю
alembic history
```

## OAuth настройка

### Google OAuth

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Google+ API
4. Credentials → Create Credentials → OAuth 2.0 Client ID
5. Тип приложения: Web application
6. Authorized redirect URIs: `http://localhost:8000/api/v1/auth/login/google/callback`
7. Скопируйте Client ID и Client Secret в `.env`

```env
GOOGLE_CLIENT_ID=ваш_client_id
GOOGLE_CLIENT_SECRET=ваш_client_secret
```

### Yandex OAuth

1. Перейдите на [Yandex OAuth](https://oauth.yandex.ru/)
2. Зарегистрируйте новое приложение
3. Платформы → Веб-сервисы
4. Callback URI: `http://localhost:8000/api/v1/auth/login/yandex/callback`
5. Права доступа: `login:email` и `login:info`
6. Скопируйте ID и Пароль приложения в `.env`

```env
YANDEX_CLIENT_ID=ваш_client_id
YANDEX_CLIENT_SECRET=ваш_client_secret
```

### VK OAuth

1. Перейдите в [VK для разработчиков](https://vk.com/apps?act=manage)
2. Создайте новое приложение (тип: Веб-сайт)
3. Настройки → Адрес сайта: `http://localhost:8000`
4. Базовый домен: `localhost`
5. Authorized redirect URI: укажите ваш ngrok URL (для локальной разработки)
6. Скопируйте ID приложения и Защищённый ключ в `.env`

```env
VK_CLIENT_ID=ваш_client_id
VK_CLIENT_SECRET=ваш_client_secret
# Для локальной разработки используйте ngrok
VK_REDIRECT_URI=https://ваш_ngrok_url/api/v1/auth/login/vk/callback
```

**Примечание**: VK требует HTTPS для redirect URI. Для локальной разработки используйте [ngrok](https://ngrok.com/):

```bash
ngrok http 8000
```

## Примеры использования

### Регистрация пользователя

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123!"
  }'
```

### Вход и получение токена

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=SecurePassword123!"
```

Ответ:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Создание задачи

```bash
curl -X POST "http://localhost:8000/api/v1/todo_items/" \
  -H "Authorization: Bearer ваш_токен" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Купить продукты",
    "description": "Молоко, хлеб, яйца",
    "category_name": "покупки",
    "date_of_execution": "2026-01-10"
  }'
```

### Получение всех задач

```bash
curl -X GET "http://localhost:8000/api/v1/todo_items/all" \
  -H "Authorization: Bearer ваш_токен"
```

## Разработка

### Код стайл

Проект использует:

- **isort** для сортировки импортов
- **PEP 8** стандарты кодирования

```bash
# Форматирование кода
make format
```

### Структура коммитов

Рекомендуется использовать [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: добавлена возможность фильтрации задач
fix: исправлена ошибка авторизации через VK
docs: обновлена документация API
```

## Лицензия

Этот проект создан в учебных целях.

## Автор

**Aleksandr Terekhov**

## Известные проблемы

- VK OAuth требует HTTPS (используйте ngrok для локальной разработки)
- При первом запуске необходимо вручную создать суперпользователя в БД

---

**Приятного использования TaskPilot!**
