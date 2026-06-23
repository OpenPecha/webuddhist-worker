from worker_api.config import get
from worker_api.notifications.models.reminder_models import UpcomingReminder


def build_notification_content(reminder: UpcomingReminder) -> tuple[str, str]:
    routine = reminder.routine_config or {}
    title = get("NOTIFICATION_DEFAULT_TITLE")
    body = get("NOTIFICATION_DEFAULT_BODY")

    if routine.get("message_template"):
        body = routine["message_template"]
    elif routine.get("plan_name"):
        body = f"Time for {routine['plan_name']}"
    elif routine.get("current_day_number") is not None:
        body = f"Day {routine['current_day_number']}: time for your practice."

    return title, body
