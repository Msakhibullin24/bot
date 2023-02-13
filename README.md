1. ```bash
   pip install -r requirements.txt
    ```
2. Создайте БД
3. Установите параметры БД в [config.py](app/config.py)
4. ```bash
    alembic upgrade head
    ```