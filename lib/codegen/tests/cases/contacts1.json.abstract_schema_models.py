from django.contrib.postgres.fields import JSONField
from django.db import models


class BaseContact(models.Model):
    uid = models.CharField(verbose_name=' uid', editable=False, primary_key=True, max_length=255)
    version = models.IntegerField(verbose_name=' version', editable=False)
    name = models.CharField(verbose_name='Наименование', editable=False, max_length=255)
    phones = JSONField(verbose_name='Phones', editable=False, null=True)
    emails = JSONField(verbose_name='Emails', editable=False, null=True)
    order_index = models.IntegerField(verbose_name='Индекс для сортировки', editable=False)

    class Meta:
        abstract = True


class BaseComment(models.Model):
    uid = models.CharField(verbose_name=' uid', editable=False, primary_key=True, max_length=255)
    version = models.IntegerField(verbose_name=' version', editable=False)
    user = models.IntegerField(verbose_name='User', editable=False)
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    message = models.CharField(verbose_name='Сообщение', editable=False, max_length=255)

    class Meta:
        abstract = True


