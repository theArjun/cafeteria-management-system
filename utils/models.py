from django.db import models


class TimeStampedModelMixin(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RemarksModelMixin(models.Model):

    remarks = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True
