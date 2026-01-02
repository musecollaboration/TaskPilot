# Тесты TaskPilot

Комплексный набор тестов для проекта TaskPilot, покрывающий все основные функции API.

## Структура тестов

```
tests/
├── __init__.py           # Инициализация пакета тестов
├── conftest.py           # Конфигурация pytest и фикстуры
├── test_auth.py          # Тесты аутентификации
├── test_todo_items.py    # Тесты CRUD операций с задачами
├── test_users.py         # Тесты пользовательских эндпоинтов
└── test_admin.py         # Тесты административной панели
```

## Покрытие тестов

### Аутентификация (`test_auth.py`)

- Регистрация пользователей
  - Успешная регистрация
  - Дублирование email/username
  - Валидация email и пароля
- Вход в систему
  - Успешный вход
  - Неправильные креденшиалы
  - Вход по username и email
- JWT токены
  - Проверка структуры токена
  - Защищенные эндпоинты
- Информация о пользователе
  - Получение профиля
  - Валидация токена

### Задачи (`test_todo_items.py`)

- Создание задач (Create)
  - С полными данными
  - С минимальными данными
  - С датой выполнения
  - Валидация категорий
- Чтение задач (Read)
  - Все задачи пользователя
  - Конкретная задача по ID
  - Изоляция данных пользователей
- Обновление задач (Update)
  - Изменение полей
  - Отметка как выполненной
  - Множественные изменения
- Удаление задач (Delete)
  - Успешное удаление
  - Защита от удаления чужих задач

### Пользователи (`test_users.py`)

- Получение списка пользователей
- Получение пользователя по ID
- Профиль пользователя
- Безопасность
  - Скрытие паролей в ответах
  - Изоляция данных между пользователями

### Администрирование (`test_admin.py`)

- Контроль доступа
  - Доступ только для админов
  - Блокировка для обычных пользователей
- Операции с задачами
  - Просмотр всех задач
  - Удаление любых задач
- Безопасность
  - Защита от повышения привилегий

## Запуск тестов

### Предварительные требования

1. Установите тестовые зависимости:

```bash
poetry install
```

2. Создайте тестовую базу данных:

```bash
psql -U postgres -c "CREATE DATABASE test_taskpilot;"
```

3. Убедитесь что PostgreSQL и Redis запущены:

```bash
make docker-u
```

### Команды запуска

#### Запустить все тесты

```bash
make test
# или
poetry run pytest
```

#### Запустить с подробным выводом

```bash
make test-v
# или
poetry run pytest -v
```

#### Запустить с отчетом о покрытии

```bash
make test-cov
# или
poetry run pytest --cov=app --cov-report=html --cov-report=term
```

После запуска откройте `htmlcov/index.html` в браузере для просмотра детального отчета.

#### Запустить конкретный файл тестов

```bash
make test-one TEST=tests/test_auth.py
# или
poetry run pytest tests/test_auth.py -v
```

#### Запустить конкретный тест

```bash
poetry run pytest tests/test_auth.py::TestAuthRegistration::test_register_new_user_success -v
```

#### Запустить тесты по маркеру

```bash
# Только unit тесты
poetry run pytest -m unit

# Только integration тесты
poetry run pytest -m integration
```

## Результаты тестов

После успешного запуска вы увидите примерно такой вывод:

```
tests/test_admin.py ........                                    [ 20%]
tests/test_auth.py ..............                               [ 55%]
tests/test_todo_items.py .................                      [ 85%]
tests/test_users.py ......                                      [100%]

==================== 45 passed in 12.34s ====================
```

## Конфигурация

### pytest.ini

Конфигурация pytest находится в файле `pytest.ini`:

- Пути к тестам
- Настройки async тестов
- Параметры покрытия кода
- Маркеры тестов

### conftest.py

Содержит фикстуры:

- `test_engine` - движок тестовой БД
- `test_session` - сессия БД для тестов
- `client` - HTTP клиент для API запросов
- `test_settings` - тестовые настройки

## Написание новых тестов

### Пример теста

```python
import pytest
from httpx import AsyncClient


class TestMyFeature:
    """Тесты новой функции."""

    async def test_something(self, client: AsyncClient):
        """Тест чего-то."""
        response = await client.get("/api/v1/endpoint")

        assert response.status_code == 200
        assert "expected_key" in response.json()
```

### Использование фикстур

```python
async def test_with_database(self, test_session: AsyncSession):
    """Тест с прямым доступом к БД."""
    # Работаем напрямую с БД через session
    pass

async def test_with_client(self, client: AsyncClient):
    """Тест через HTTP клиент."""
    # Делаем HTTP запросы
    response = await client.get("/api/v1/endpoint")
```

### Вспомогательные функции

```python
async def create_user_and_login(client: AsyncClient) -> str:
    """Создает пользователя и возвращает токен."""
    await client.post("/api/v1/auth/register", json={...})
    response = await client.post("/api/v1/auth/login", data={...})
    return response.json()["access_token"]
```

## Отладка тестов

### Запуск с отладочным выводом

```bash
poetry run pytest -v -s tests/test_auth.py
```

### Остановка на первой ошибке

```bash
poetry run pytest -x
```

### Показать локальные переменные при ошибке

```bash
poetry run pytest -l
```

### Запуск последних упавших тестов

```bash
poetry run pytest --lf
```

## Тестовая база данных

Тесты используют отдельную тестовую БД для изоляции от основной:

```python
TEST_DATABASE_URL = "postgresql+asyncpg://admin:admin1234@localhost:5432/test_taskpilot"
```

База автоматически очищается после каждого теста через фикстуры в `conftest.py`.

## CI/CD Integration

Тесты можно легко интегрировать в CI/CD pipeline:

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: admin1234
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
      redis:
        image: redis:7

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - name: Install dependencies
        run: poetry install
      - name: Run tests
        run: poetry run pytest --cov=app
```

## Best Practices

1. **Изоляция тестов** - каждый тест независим от других
2. **Чистая БД** - БД очищается перед каждым тестом
3. **Понятные имена** - названия тестов описывают что проверяется
4. **Arrange-Act-Assert** - структура тестов
5. **Фикстуры** - переиспользование кода через фикстуры
6. **Async/Await** - правильная работа с асинхронным кодом

## Метрики покрытия

Цель: **покрытие кода тестами > 80%**

Проверить текущее покрытие:

```bash
make test-cov
```

Исключения из покрытия (указаны в `pytest.ini`):

- Миграции
- Конфигурационные файлы
- `__init__.py` файлы

## Contributing

При добавлении новой функциональности:

1. Напишите тесты **до** реализации (TDD)
2. Покройте тестами успешные сценарии
3. Покройте тестами ошибочные сценарии
4. Проверьте покрытие кода
5. Убедитесь что все тесты проходят

---

