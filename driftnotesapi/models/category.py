from django.db import models


class Category(models.Model):

    name = models.CharField(max_length=55)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
