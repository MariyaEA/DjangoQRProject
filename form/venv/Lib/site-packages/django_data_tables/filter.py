from datetime import datetime, timedelta

from django import forms
from django.db.models import Q

from django_data_tables.table import DataTableFilter


class IntFilter(DataTableFilter):
    field_class = forms.IntegerField

    def get_q_expression(self, data):
        data = self.get_value(data)
        if data is not None:
            return Q(**{"{}".format(self.field): data})
        return None


class DateFilter(DataTableFilter):
    sortable = True
    field_class = forms.DateField
    field_params = {
        'widget': forms.DateInput(attrs={'type': 'date'}),
        'required': False
    }
    greater = True
    equal = True
    with_time = True

    def get_value(self, data):
        date = super().get_value(data)
        if not date:
            return None
        if self.with_time:
            if self.greater:
                date = datetime.combine(date, datetime.min.time())
                if not self.equal:
                    date += timedelta(days=1)
            else:
                date = datetime.combine(date, datetime.max.time())
                if not self.equal:
                    date -= timedelta(days=1)
        return date

    def get_q_expression(self, data):
        data = self.get_value(data)
        if data is None:
            return None
        operation = 'gt' if self.greater else 'lt'
        if self.equal:
            operation += 'e'
        return Q(**{'{}__{}'.format(self.field, operation): data})
