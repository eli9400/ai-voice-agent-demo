import time

from app.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.process_mock_ai_message")
def process_mock_ai_message(content: str) -> dict[str, str]:
    time.sleep(3)
    return {
        "input": content,
        "assistant_message": f"Async mock AI response: {content}",
    }
