from django.db import models

# Create your models here.


class Actor(models.Model):
    name = models.CharField(max_length=255)
    name_normalized = models.CharField(
        max_length=255, db_index=True)
    csfd_url = models.URLField(unique=True)

    def __str__(self):
        return self.name


class Film(models.Model):
    rank = models.PositiveSmallIntegerField(unique=True)
    title = models.CharField(max_length=255)
    title_normalized = models.CharField(
        max_length=255, db_index=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    csfd_url = models.URLField(unique=True)
    actors = models.ManyToManyField(Actor, related_name='films')

    def __str__(self):
        return f'#{self.rank} {self.title}'

    class Meta:
        ordering = ['rank']
