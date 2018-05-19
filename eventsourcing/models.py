import logging

from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords

from core.models import Dated, PUided, Versioned, Owned
from .consts import SUBSCRIPTION_TYPES

LOGGER = logging.getLogger(__name__)


class Subscription(PUided, Dated, Versioned, Owned):
    name = models.CharField(max_length=255)
    type = models.IntegerField(choices=SUBSCRIPTION_TYPES)
    settings = JSONField()
    events = ArrayField(models.CharField(max_length=200))

    history = HistoricalRecords()

    class Meta:
        unique_together = (('name', 'type'), )
        verbose_name = _("Подписка")
        verbose_name_plural = _("Подписки")


def subscribe(user, name, type_, settings, events):
    obj, is_new = Subscription.objects.get_or_create(
        {'settings': settings, 'events': events, 'user': user},
        name=name, type=type_)

    if is_new:
        return obj

    if obj.user != user:
        raise ValueError('You are trying update not your subscription')

    extra_events = [x for x in events if x not in obj.events]

    if not extra_events and obj.settings == settings:
        return obj

    obj.settings = settings
    obj.events.extend(extra_events)
    obj.save()
    return obj


def unsubscribe(user, name, type_, events):
    obj, is_new = Subscription.objects.get_or_create(
        {'settings': {}, 'events': [], 'user': user},
        name=name, type=type_)

    if is_new:
        return obj

    if obj.user != user:
        raise ValueError('You are trying update not your subscription')

    new_events = [x for x in obj.events if x not in events]

    if new_events == obj.events:
        return obj

    obj.events = new_events
    obj.save()
    return obj


# TODO(meteozond): I think it is more expedient connect to the signal in
# the decorated models.


@receiver(post_save, dispatch_uid='post-save-historical-model')
def _post_save_historical_model(sender, instance, created, **kwargs):
    """
    Automatically triggers "created" and "updated" actions.
    """
    from .replicator.registry import _is_replicating_historical_model  # noqa
    if not _is_replicating_historical_model(instance):
        return
    if not created:
        raise RuntimeError('Historical changes detected! WTF?')

    from eventsourcing.utils import _get_event_names  # noqa
    events = _get_event_names(instance)
    subscribers = Subscription.objects.filter(events__overlap=events)
    if subscribers.exists():
        LOGGER.info('replicate %s [hist=%s]', events[-1], instance.history_id)
        from .replicator import replicate  # noqa
        replicate(instance)