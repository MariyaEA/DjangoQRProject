from django import template

register = template.Library()

def render_data_table_column(column, item):
    return column.render(item)

register.filter(render_data_table_column)
