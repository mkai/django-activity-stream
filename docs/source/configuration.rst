Configuration
==============

Update these settings in your project's ``settings.py``.  Supported settings are defined below.

Action Template
***************

``ACTSTREAM_ACTION_TEMPLATE = 'activity/single_action.txt'``

String template name. Only used if ``USE_I18N = True`` in your settings.
Name of the template to use when formatting an Action for unicode.

Templates can use the `i18n framework <https://docs.djangoproject.com/en/dev/topics/i18n/internationalization/#specifying-translation-strings-in-template-code>`_.


Stream Modules
**************

``ACTSTREAM_MANAGER = 'actstream.managers.ActionManager'``

The name of the manager to use for ``Action.objects``.
Add your own manager here to create custom streams.

For more info, see :ref:`custom-streams`
