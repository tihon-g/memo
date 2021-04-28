from django.db import transaction
from django.db.models import signals
from django.dispatch import receiver

from render.models import Order
from render.tasks import process_order_render


@receiver(signals.post_save, sender=Order)
def order_post_save(instance, **kwargs):
    worker_id = instance.worker.id if instance.worker else None

    if instance.running is False and instance.renders_done < instance.N:
        transaction.on_commit(lambda: process_order_render.delay(instance.id, worker_id))
