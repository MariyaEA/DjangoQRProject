from datetime import datetime, date, time

from django.template import Template, Context, loader

from django_data_tables.table import DataTableColumn


class ModelFieldColumn(DataTableColumn):
    sortable = True
    template = "{{ field }}"
    title = None

    def __init__(self, field_name, title=None, template=None):
        if template is not None:
            self.template = template
        if not title:
            if self.title:
                title = self.title
            else:
                title = field_name.capitalize()
        super().__init__(title)
        self.field_name = field_name

    def get_context(self, item):
        c = {'field': getattr(item, self.field_name), 'object': item}
        return Context(c)

    def get_template(self):
        return Template(self.template)

    def render(self, table, item):
        context = self.get_context(item)
        template = self.get_template()
        return template.render(context)


class DateTimeColumn(ModelFieldColumn):
    format = "%Y-%m-%d %H:%M:%S"

    def __init__(self, field_name, title=None, template=None, format=None):
        if format:
            self.format = format
        super().__init__(field_name, title, template)

    def get_context(self, item):
        field = getattr(item, self.field_name)
        if not isinstance(field, (datetime, date, time)):
            raise ValueError(
                'DateTimeColumn expects a datetime, date or time field'
            )
        c = {'field': field.strftime(self.format), 'object': item}
        return Context(c)


class FkFieldColumn(ModelFieldColumn):
    title = 'optional Fk'
    template = (
        '{% if field %}FKModel #{{ field.pk }}{% else %}not set{% endif %}'
    )


class ActionColumn(DataTableColumn):
    sortable = False

    def render(self, table, item):
        t = loader.get_template('django_data_tables/action_column.html')
        return t.render({'item': item, 'table': table})


class IdColumn(ModelFieldColumn):
    def render(self, table, item):
        return "{}".format(item.pk)
