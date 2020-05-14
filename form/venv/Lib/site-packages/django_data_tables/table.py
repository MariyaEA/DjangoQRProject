import inspect
import json
import math

from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ValidationError
from django.forms import BaseForm
from django.http import HttpResponse, HttpResponseRedirect
from django.apps import apps
from django.db import models
from django.forms.widgets import Media
from django.template.loader import get_template
from django.template import Template, RequestContext
from django.urls import reverse
from django import forms


class UseMediaMixin(object):
    @property
    def media(self):
        """
        Mixin to add behaviour of Media metaclass like in django Forms
        """
        if hasattr(self, 'Media'):
            js = getattr(self.Media, 'js', [])
            css = getattr(self.Media, 'css', {})
            media = Media(js=js, css=css)
        else:
            media = Media()
        return media

    @classmethod
    def get_media(cls):
        """
        Mixin to add behaviour of Media metaclass like in django Forms
        """
        if hasattr(cls, 'Media'):
            js = getattr(cls.Media, 'js', [])
            css = getattr(cls.Media, 'css', {})
            media = Media(js=js, css=css)
        else:
            media = Media()
        return media


class BaseDataTableRenderer(UseMediaMixin):
    def __init__(self, data_table, request, *args, **kwargs):
        self.data_table = data_table
        self.request = request

    def __repr__(self):
        return "<Table Renderer for model: '{}' with {} instances>"\
            .format(self.data_table.model, self.data_table.get_queryset(None).count())

    @property
    def media(self):
        media = super().media
        for action in self.data_table.actions:
            media = media + action.get_media()
        for key, _filter in self.data_table.filters.items():
            media = media + _filter.media
        for column in self.data_table.columns:
            media = media + column.media
        return media


class TemplateDataTableRenderer(BaseDataTableRenderer):
    template = 'django_data_tables/django_data_table.html'

    class Media:
        js = ('django_data_tables/django_data_tables.js',)
        css = {'all': ('django_data_tables/django_data_tables.css',)}

    def __repr__(self):
        template = get_template(self.template)
        return template.render(
            context={'table': self.data_table},
            request=self.request
        )


class DataTableAction(UseMediaMixin):
    name = 'unnamed action'
    title = None
    is_single = False
    abort_button = 'Ok'
    submit_button = None
    only_get = True

    def __init__(self, data_table):
        if self.title is None:
            self.title = self.name
        self.data_table = data_table

    @classmethod
    def ident(cls):
        return "{}.{}".format(cls.__module__, cls.__name__)

    def is_available(self, request, obj=None):
        return True

    def get(self, request, objs):
        raise NotImplementedError(
            'Please implement a get function for {}'
            .format(self.ident())
        )

    def post(self, request, objs):
        raise NotImplementedError(
            'Please implement a post function for {}'
            .format(self.ident())
        )


class DataTableRedirectAction(DataTableAction):
    is_single = True
    abort_button = 'Cancel'
    submit_button = 'Ok'

    def get(self, request, obj):
        return HttpResponseRedirect(
            self.get_redirect_url(request, obj)
        )

    def get_redirect_url(self, request, obj):
        raise NotImplementedError(
            'Please implement a get_redirect_url function for {}'
            .format(self.ident())
        )


class FormAction(DataTableAction):
    is_single = True
    form_class = None
    abort_button = 'Abort'
    submit_button = 'Submit'
    only_get = False

    def get(self, request, objs):
        form = self.get_form(None, instance=objs[0])
        return self.get_template().render(
            context=RequestContext(request, {'form': form})
        )

    def post(self, request, objs):
        form = self.get_form(request.POST, instance=objs[0])
        if form.is_valid():
            return self.success(form, objs[0])
        return self.get_template().render(
            context=RequestContext(request, {'form': form})
        )

    def get_template(self):
        return Template('{% csrf_token %}{{ form }}')

    def get_form(self, data, instance):
        if not issubclass(self.form_class, BaseForm):
            raise ValueError(
                'Please define a form_class for {}'
                .format(self.ident())
            )
        return self.form_class(data, instance=instance)



class DataTableColumn(UseMediaMixin):
    sortable = False

    class Media:
        pass

    def __init__(self, title):
        self.title = title

    def render(self, table, item):
        return "{}".format(item)


class TableFilterForm(forms.Form):

    def __init__(self, _filter):
        super().__init__()
        self.label = _filter.label
        self.field = _filter.field_class(
            **_filter.field_params
        )
        self.fields[self.label] = self.field

    def get_value(self, data):
        data = data.get(self.label)
        if data is None:
            return None
        try:
            return self.field.clean(data)
        except ValidationError:
            return None


class DataTableFilter(UseMediaMixin):
    field_class = forms.CharField
    field_params = {'required': False}

    def __init__(self, field, **kwargs):
        self.field = field
        for key, value in kwargs.items():
            setattr(self, key, value)
        if not hasattr(self, 'label'):
            self.label = self.field
        self.form = TableFilterForm(self)

    def get_value(self, data):
        data = json.loads(data)
        return self.form.get_value(data)

    def get_q_expression(self, data):
        if self.field is None:
            return None
        value = self.get_value(data)
        if not value:
            return None
        return models.Q(**{"{}__icontains".format(self.field): value})



class DataTable(object):
    model = None
    _name = None
    renderer = TemplateDataTableRenderer
    actions = []
    filters = {}
    columns = []
    columns_by_title = {}
    css_prefix = 'ddt'
    item_name = 'item'
    item_name_plural = None
    _renderer_instance = None

    def __init__(self, *args, **kwargs):
        if not self.columns_by_title:
            self.initalize_class()

    def initalize_class(self):
        self.model = self._get_model()
        initalized_actions = []
        for action_class in self.actions:
            if not issubclass(action_class, DataTableAction):
                raise ImproperlyConfigured(
                    "action class '{}' must inherit from "
                    "django_data_tables.DataTableAction to be used in {}"
                    .format(action_class, self.__class__)
                )
            initalized_actions.append(action_class(self))
        self.actions = initalized_actions
        for column in self.columns:
            if not isinstance(column, DataTableColumn):
                raise ImproperlyConfigured(
                    "column class '{}' must inherit from "
                    "django_data_tables.DataTableColumn to be used in {}"
                    .format(column.__class__, self.__class__)
                )
            if column.title in self.columns_by_title.keys():
                raise ImproperlyConfigured(
                    "column title '{}' may only be used once per Table"
                    .format(column.title)
                )
            self.columns_by_title[column.title] = column
        for key, _filter in self.filters.items():
            if not isinstance(_filter, DataTableFilter):
                raise ImproperlyConfigured(
                    "filter '{}' with class '{}' must inherit from "
                    "django_data_tables.DataTableFliter to be used in {}"
                    .format(key, _filter.__class__, self.__class__)
                )
        if self.item_name_plural is None:
            self.item_name_plural = self.item_name + 's'

    @classmethod
    def ident(cls):
        if cls._name is None:
            cls._name = "{}.{}".format(cls.__module__, cls.__name__)
        return cls._name

    def get_column(self, title):
        try:
            return self.columns_by_title[title]
        except IndexError:
            raise IndexError(
                'called get_column with unregistered column title: "{}"'
                .format(title)
            )

    def get_action(self, action_ident):
         for action in self.actions:
             if action.ident() == action_ident:
                 return action
         raise ValueError(
             'no Action with Identifier "{}" found'.format(action_ident)
         )

    def get_renderer(self, request, *args, **kwargs):
        if self._renderer_instance is None:
            if not issubclass(self.renderer, BaseDataTableRenderer):
                raise ImproperlyConfigured(
                    "renderer must be inherited from "
                    "django_data_tables.BaseDataTableRenderer"
                )
            self._renderer_instance = self.renderer(
                self,
                request,
                *args,
                **kwargs
            )
        return self._renderer_instance

    def get_queryset(self, request):
        if self.model is None:
            raise ImproperlyConfigured(
                'please specify a model or an explicit get_queryset method '
                'for {}'.format(self.__class__)
            )
        return self.model.objects.all()

    def run_filters(self, request, qs):
        for key, _filter in self.filters.items():
            data = self.get_request_param(request, key)
            if data is None:
                continue
            q_function = _filter.get_q_expression(data)
            if q_function is not None:
                qs = qs.filter(q_function)
        return qs

    def _get_model(self):
        if self.model is None:
            return None
        if inspect.isclass(self.model) and issubclass(self.model, models.Model):
            return self.model
        if isinstance(self.model, ("".__class__, u"".__class__)):
            if len(self.model.split('.')) != 2:
                raise ImproperlyConfigured(
                    'model format should be "< app_name >.< model_name >'
                )
            app_name, model_name = self.model.split('.')
            return apps.get_model(app_name, model_name)
        raise ImproperlyConfigured(
            'model should be None, django.db.models.Model class or a string'
        )

    def get_request_param(self, request, key, default=None):
        return request.GET.get(key, request.POST.get(key, default))

    def get_request_params(self, request, keys):
        results = []
        for key in keys:
            results.append(int(self.get_request_param(request, key, 0)))
        return results

    def get_objects(self, request):
        queryset = self.run_filters(
            request,
            self.get_queryset(request)
        )
        ids = json.loads(self.get_request_param(request, 'ids', "[]"))
        if ids:
            queryset = queryset.filter(pk__in=ids)
        return queryset

    def get_data(self, request):
        rows = []
        queryset = self.get_queryset(request)
        total = queryset.count()
        queryset = self.run_filters(request, queryset)
        filtered = queryset.count()
        try:
            limit, requested_offset, page = self.get_request_params(
                request,
                ['limit', 'offset', 'page']
            )
        except ValueError as e:
            return HttpResponse(
                "limit, offset and page must be integers",
                status=400
            )
        pages = math.ceil(filtered / limit)
        if not page:
            # if no page is requested then get page by requested offset
            page = math.ceil(max(requested_offset + 1, 1) / limit)
        page = min(page, pages)
        # returned offset is always calculated by page to ensure that its valid
        offset = (page - 1) * limit
        sort_by = self.get_request_param(request, 'sort_by', '')
        if sort_by:
            try:
                order_by = self.get_column(sort_by).field_name
            except IndexError:
                return HttpResponse(
                    'unknown column title: "{}"'.format(sort_by),
                    status=400
                )
            sort_asc = self.get_request_param(request, 'sort_dir', 'asc') == 'asc'
            if not sort_asc:
                order_by = '-{}'.format(order_by)
            queryset = queryset.order_by(order_by)
        if queryset.exists():
            sliced = queryset[offset: offset+limit]
            for item in sliced:
                row = []
                for column in self.columns:
                    row.append(column.render(self, item))
                rows.append(row)
        data = {
            'rows': rows,
            'filtered': filtered,
            'total': total,
            'pages': pages,
            'page': page
        }
        return HttpResponse(json.dumps(data))

    def callback_urls(self):
        urls = {
            'data': reverse('ddt-get_data', args=[self.ident()]),
            'action': reverse('ddt-action', args=[self.ident()])
        }
        return json.dumps(urls)
