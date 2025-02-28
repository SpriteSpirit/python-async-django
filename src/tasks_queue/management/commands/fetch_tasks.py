import time
from threading import Thread

from django.core.management.base import BaseCommand
from django.db import transaction

from tasks_queue.models import TaskQueue


def fetch_task() -> TaskQueue | None:
    """
    Функция для извлечения задачи из очереди.
    """

    # создание атомарной транзакции
    with transaction.atomic():
        task = (
            TaskQueue.objects.select_for_update(skip_locked=True)
            .filter(status="pending")
            .order_by("created_at")
            .first()
        )

        if task:
            task.status = "in_progress"
            task.save()

            return task

        return None


def worker(worker_id: int) -> None:
    """
    Функционал воркера (имитация обработки задачи)
    """

    # Бесконечный цикл для обработки задач
    while True:
        task = fetch_task()
        if task:
            print(f"Worker {worker_id} взял задачу: {task.task_name}")
            time.sleep(2)

            with transaction.atomic():
                task.status = "completed"
                task.save()
            print(f"Worker {worker_id} завершил задачу: {task.task_name}")
        else:
            print(f"Worker {worker_id}: Нет задач для обработки.")
            # Выход из цикла, если задач нет
            break


class Command(BaseCommand):
    help = "Запускает воркеров для обработки задач."

    def handle(self, *args, **kwargs):
        # Создание нескольких потоков
        threads = []

        # Запуск воркеров в отдельных потоках
        for i in range(5):
            thread = Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Ожидание завершения всех потоков
        for thread in threads:
            thread.join()

        self.stdout.write(self.style.SUCCESS("Все воркеры завершили работу."))
