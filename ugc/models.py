from django.db import models

class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='Id пользователя',
        unique=True
    )
    name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=255,
        null=True
    )

    def __str__(self):
        return f'#{self.external_id} {self.name}'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Place(models.Model):
    profile = models.ForeignKey(
        to='ugc.Profile',
        verbose_name='Профиль',
        on_delete=models.PROTECT,
    )
    name = models.CharField(
        verbose_name='Название места',
        max_length=255,
    )
    lat = models.FloatField(
        verbose_name='Широта',
    )
    lon = models.FloatField(
        verbose_name='Долгота'
    )
    file_id = models.TextField(
        verbose_name='ID фото',
    )

    def __str__(self):
        return f'Место {self.pk} от {self.profile}'

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'

