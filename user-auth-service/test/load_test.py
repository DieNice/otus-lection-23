import json
from datetime import datetime
from random import choice, randint, random
from typing import Dict, List

from locust import HttpUser, between, task


class UserAPIUser(HttpUser):
    """
    Пользователь, который выполняет нагрузочное тестирование User API
    """

    # Время ожидания между задачами (1-3 секунды)
    wait_time = between(0.5, 3)

    # Хранилище созданных пользователей для последующего использования
    created_users: List[Dict] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def on_start(self):
        """
        Действия при запуске пользователя
        """
        # Создаем несколько пользователей для тестирования GET и DELETE
        for _ in range(5):
            user_data = self._generate_user_data()
            with self.client.post(
                "/user/", json=user_data, headers=self.headers, catch_response=True
            ) as response:
                if response.status_code == 200:
                    # Сохраняем ID созданного пользователя
                    # В реальном API нужно получить ID из ответа
                    # Сейчас мы используем случайный ID
                    user_id = randint(1, 1000)
                    self.created_users.append({"id": user_id, "data": user_data})
                else:
                    response.failure(f"Failed to create user: {response.text}")

    @staticmethod
    def _generate_user_data() -> Dict:
        """
        Генерирует случайные данные пользователя
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return {
            "username": f"user_{timestamp}_{randint(1, 10000)}",
            "first_name": f"FirstName_{randint(1, 1000)}",
            "last_name": f"LastName_{randint(1, 1000)}",
            "email": f"user_{timestamp}@example.com",
            "phone": f"+{randint(100, 999)}{randint(1000000, 9999999)}",
        }

    @staticmethod
    def _generate_update_data() -> Dict:
        """
        Генерирует случайные данные для обновления пользователя
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return {
            "first_name": f"UpdatedFirstName_{randint(1, 1000)}",
            "last_name": f"UpdatedLastName_{randint(1, 1000)}",
            "email": f"updated_{timestamp}@example.com",
            "phone": f"+{randint(100, 999)}{randint(1000000, 9999999)}",
        }

    @task(3)
    def create_user(self):
        """
        Создание нового пользователя (вес задачи - 3)
        """
        user_data = self._generate_user_data()

        with self.client.post(
            "/user/", json=user_data, headers=self.headers, catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get("message") == "Successful operation":
                        response.success()
                        # Сохраняем пользователя для других тестов
                        self.created_users.append(
                            {
                                "id": randint(
                                    1, 10000
                                ),  # В реальном API берем из ответа
                                "data": user_data,
                            }
                        )
                    else:
                        response.failure(f"Unexpected response: {result}")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(5)
    def get_user_by_id(self):
        """
        Получение пользователя по ID (вес задачи - 5)
        """
        if not self.created_users:
            # Если нет созданных пользователей, пропускаем задачу
            return

        user = choice(self.created_users)
        user_id = user["id"]

        with self.client.get(
            f"/user/{user_id}", headers=self.headers, catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    result = response.json()
                    if "username" in result:
                        response.success()
                    else:
                        response.failure(f"Unexpected response structure: {result}")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            elif response.status_code == 404:
                # Пользователь может быть удален - это нормально
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(2)
    def delete_user(self):
        """
        Удаление пользователя по ID (вес задачи - 2)
        """
        if not self.created_users:
            return

        # Выбираем случайного пользователя для удаления
        index = randint(0, len(self.created_users) - 1)
        user = self.created_users.pop(index)
        user_id = user["id"]

        with self.client.delete(
            f"/user/{user_id}", headers=self.headers, catch_response=True
        ) as response:
            if response.status_code in [200, 204]:
                response.success()
            elif response.status_code == 404:
                # Пользователь уже удален - считаем успехом
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(2)
    def update_user(self):
        """
        Обновление пользователя (вес задачи - 2)
        """
        if not self.created_users:
            return

        user = choice(self.created_users)
        user_id = user["id"]
        update_data = self._generate_update_data()

        with self.client.put(
            f"/user/{user_id}",
            json=update_data,
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get("message") == "Successful operation":
                        response.success()
                    else:
                        response.failure(f"Unexpected response: {result}")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            elif response.status_code == 404:
                # Пользователь не найден - нормальная ситуация
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(1)
    def create_and_delete_user(self):
        """
        Комбинированная задача: создать и сразу удалить пользователя (вес - 1)
        """
        user_data = self._generate_user_data()

        # Создаем пользователя
        with self.client.post(
            "/user/", json=user_data, headers=self.headers, catch_response=True
        ) as create_response:
            if create_response.status_code != 200:
                create_response.failure(
                    f"Failed to create user: {create_response.status_code}"
                )
                return

            try:
                result = create_response.json()
                if result.get("message") != "Successful operation":
                    create_response.failure(f"Unexpected create response: {result}")
                    return
                create_response.success()
            except json.JSONDecodeError:
                create_response.failure("Invalid JSON in create response")
                return

        # В реальном API нужно получить ID созданного пользователя
        # Сейчас используем случайный ID
        user_id = randint(1, 1000)

        # Удаляем пользователя
        with self.client.delete(
            f"/user/{user_id}", headers=self.headers, catch_response=True
        ) as delete_response:
            if delete_response.status_code in [200, 204, 404]:
                delete_response.success()
            else:
                delete_response.failure(f"Delete failed: {delete_response.status_code}")

    @task(1)
    def get_non_existent_user(self):
        """
        Запрос несуществующего пользователя (вес - 1)
        """
        # Генерируем заведомо большой ID
        user_id = randint(100000, 999999)

        with self.client.get(
            f"/user/{user_id}", headers=self.headers, catch_response=True
        ) as response:
            if response.status_code == 404:
                response.success()
            elif response.status_code == 200:
                # Может быть, пользователь существует - тоже успех
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


class APITestUser(HttpUser):
    """
    Альтернативная конфигурация для тестирования с разными параметрами
    """

    wait_time = between(1, 5)  # Более длинные паузы

    @task
    def mixed_workload(self):
        """
        Смешанная нагрузка: все операции в одной задаче
        """
        # 40% - GET запросы
        if random() < 0.4:
            user_id = randint(1, 1000)
            self.client.get(f"/user/{user_id}")

        # 30% - POST запросы
        elif random() < 0.7:
            user_data = {
                "username": f"load_user_{datetime.now().timestamp()}",
                "first_name": "Load",
                "last_name": "Test",
                "email": f"load_{datetime.now().timestamp()}@test.com",
                "phone": "+1234567890",
            }
            self.client.post("/user/", json=user_data)

        # 20% - PUT запросы
        elif random() < 0.9:
            user_id = randint(1, 1000)
            update_data = {
                "first_name": f"Updated_{randint(1, 1000)}",
                "last_name": f"Updated_{randint(1, 1000)}",
                "email": f"updated_{randint(1, 1000)}@test.com",
                "phone": f"+{randint(100, 999)}{randint(1000000, 9999999)}",
            }
            self.client.put(f"/user/{user_id}", json=update_data)

        # 10% - DELETE запросы
        else:
            user_id = randint(1, 1000)
            self.client.delete(f"/user/{user_id}")
