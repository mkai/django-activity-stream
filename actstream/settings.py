from django.conf import settings

MANAGER_MODULE = getattr(settings, 'ACTSTREAM_MANAGER', 
    'actstream.managers.ActionManager')
a, j = MANAGER_MODULE.split('.'), lambda l: '.'.join(l)
MANAGER_MODULE = getattr(__import__(j(a[:-1]), {}, {}, [a[-1]]), a[-1])
