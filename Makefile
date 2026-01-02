# Имя основного файла приложения
APP_MODULE=app.main:app
HOST=127.0.0.1
PORT=8000
API_PREFIX=/api/v1

# Makefile для управления проектом FastAPI
help:
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[1;32m%-15s\033[0m %s\n", $$1, $$2}'


run:	## Запустить сервер FastAPI (make run)
	@echo "\033[1;36mСервер запущен по адресу: http://$(HOST):$(PORT)\033[0m"
	@echo "\033[1;36mДокументация доступна по адресу: http://$(HOST):$(PORT)$(API_PREFIX)/docs\033[0m"
	poetry run uvicorn $(APP_MODULE) --reload --host $(HOST) --port $(PORT)


k-port:	## Остановить процесс на порту (make k-port)
	@echo "Остановка сервера на порту $(PORT)"
	@fuser -k $(PORT)/tcp || true


list:	## Показать все установленные пакеты poetry (make list)
	@echo "Список установленных пакетов:"
	poetry show


add:	## Добавить пакет через poetry (make add LIB=fastapi)
	@echo "Добавление пакета $(LIB)"
	poetry add $(LIB)  


add-dev:	## Добавить пакет в dev-зависимости (make add-dev LIB=pytest)
	@echo "Добавление пакета $(LIB) в dev-зависимости"
	poetry add --group dev $(LIB)

del:	## Удалить пакет через poetry (make del LIB=fastapi)
	@echo "Удаление пакета $(LIB)"
	poetry remove $(LIB)


format:	## Форматировать код с помощью (make format)
	@echo "Форматирование кода с isort"
	poetry run isort .


clean:	## Очистить временные файлы (make clean)
	@echo "Очистка временных файлов"
	find . -type d -name "__pycache__" -exec rm -r {} +


test:	## Запустить все тесты (make test)
	@echo "Запуск тестов"
	poetry run pytest


test-v:	## Запустить тесты с подробным выводом (make test-v)
	@echo "Запуск тестов с подробным выводом"
	poetry run pytest -v


test-cov:	## Запустить тесты с покрытием кода (make test-cov)
	@echo "Запуск тестов с отчетом о покрытии"
	poetry run pytest --cov=app --cov-report=html --cov-report=term


test-watch:	## Запустить тесты в режиме наблюдения (make test-watch)
	@echo "Запуск тестов в режиме наблюдения"
	poetry run pytest-watch


test-one:	## Запустить конкретный тест (make test-one TEST=tests/test_auth.py)
	@echo "Запуск теста: $(TEST)"
	poetry run pytest $(TEST) -v


mig:	## Выполнить миграции (make mig M=Добавить описание миграции)
	@echo "Выполнение миграций базы данных"
	alembic revision --autogenerate -m "$(M)"


mig-up:	## Применить миграции (make mig-up)
	@echo "Применение миграций базы данных"
	alembic upgrade head


docker-u:	## Запустить Docker контейнеры (make docker-u)
	@echo "Запуск Docker контейнеров"
	docker-compose up -d


docker-d:	## Остановить Docker контейнеры (make docker-d)
	@echo "Остановка Docker контейнеров"
	docker-compose down