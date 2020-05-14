import logging
import inspect

from django.conf import settings

from django_data_tables import DataTable, POOL

_logger = logging.getLogger(__name__)

def autodiscover():
    _logger.debug('building ddt pool...')
    apps = [app for app in settings.INSTALLED_APPS if not 'django' in app]
    for app in apps:
        try:
            module_name = '{}.tables'.format(app)
            module = getattr(__import__(module_name), 'tables')
            items = [
                member[1] for member in inspect.getmembers(module)
                if inspect.isclass(member[1]) and
                member[1].__module__.startswith(module_name)
            ]
            for item in items:
                if not inspect.isclass(item):
                    continue
                if issubclass(item, DataTable):
                    ident = item.ident()
                    if ident not in POOL.keys():
                        POOL[ident] = item()
        except ImportError:
            continue


