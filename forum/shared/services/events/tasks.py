from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from celery import shared_task
import logging

logger = logging.getLogger("comment_events")

@shared_task
def log_event(labes, data):
    logger.info(f"[{labes}] {data}")

def send_comment_to_ws(comment_data: dict):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "comments",
        {
            "type": "comment_created",
            "data": comment_data
        }
    )