## Запуск тестов

Установить зависимости:

`pip install pytest pytest-asyncio pytest-cov aiosqlite locust`

Запустить тесты с покрытием:

`pytest tests/ --cov=src --cov-report=html`

HTML-отчёт о покрытии будет в папке `htmlcov/index.html`.

Текущее покрытие: **91%**

## Нагрузочное тестирование

Требует запущенного сервера. 

Запустить Locust:

`locust -f locustfile.py --host=http://localhost:8000`

Открыть браузер: `http://localhost:8089`

Настроить количество пользователей и запустить тест.

### Сценарии нагрузки

- **create_link** — создание ссылок
- **redirect_link** — редиректы
- **redirect_nonexistent** — запросы несуществующих ссылок