from django.contrib import admin
from actstream.models import Action

class ActionAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_display = ('__unicode__', 'actor', 'verb', 'target')
    list_editable = ('verb', )
    list_filter = ('timestamp', )

admin.site.register(Action, ActionAdmin)
