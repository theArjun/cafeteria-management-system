from django.db import models


class PercentField(models.FloatField):
    def __init__(self, verbose_name='Percentage Field', name=None, min_value=0.0, max_value=100.0, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.FloatField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super(PercentField, self).formfield(**defaults)
