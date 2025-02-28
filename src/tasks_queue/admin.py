from django.contrib import admin
from tasks_queue.models import TaskQueue


@admin.register(TaskQueue)
class TaskAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления задачами в очереди.
    """

    list_display = ("task_name", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("task_name",)
