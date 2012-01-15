from datetime import datetime
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from actstream.settings import TEMPLATE, MANAGER_MODULE
from actstream.signals import action


class Action(models.Model):
    """
    Action model describing the actor acting out a verb (on an optional 
    target). 
    
    Nomenclature based on http://activitystrea.ms/specs/atom/1.0/

    Generalized Format::
    
        <actor> <verb> <time>
        <actor> <verb> <target> <time>
        <actor> <verb> <action_object> <target> <time>

    Examples::

        <justquick> <reached level 60> <1 minute ago>
        <brosner> <commented on> <pinax/pinax> <2 hours ago>
        <washingtontimes> <started follow> <justquick> <8 minutes ago>
        <mitsuhiko> <closed> <issue 70> on <mitsuhiko/flask> <3 hours ago>

    Unicode Representation::

        justquick reached level 60 1 minute ago
        mitsuhiko closed issue 70 on mitsuhiko/flask 3 hours ago

    HTML Representation::

        <a href="http://oebfare.com/">brosner</a> commented on <a href="http://github.com/pinax/pinax">pinax/pinax</a> 2 hours ago

    """
    actor_content_type = models.ForeignKey(ContentType, related_name='actor')
    actor_object_id = models.CharField(max_length=255)
    actor = generic.GenericForeignKey('actor_content_type', 'actor_object_id')

    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    target_content_type = models.ForeignKey(ContentType, related_name='target',
        blank=True, null=True)
    target_object_id = models.CharField(max_length=255, blank=True, null=True)
    target = generic.GenericForeignKey('target_content_type', 
        'target_object_id')

    action_object_content_type = models.ForeignKey(ContentType, 
        related_name='action_object', blank=True, null=True)
    action_object_object_id = models.CharField(max_length=255, blank=True, 
        null=True)
    action_object = generic.GenericForeignKey('action_object_content_type', 
        'action_object_object_id')

    timestamp = models.DateTimeField(default=datetime.now)

    public = models.BooleanField(default=True)

    objects = MANAGER_MODULE()

    class Meta:
        ordering = ('-timestamp',)

    def __unicode__(self):
        if settings.USE_I18N:
            return render_to_string(TEMPLATE, {'action': self}).strip()
        if self.target:
            if self.action_object:
                return u'%s %s %s on %s %s ago' % (self.actor, self.verb, self.action_object, self.target, self.timesince())
            else:
                return u'%s %s %s %s ago' % (self.actor, self.verb, self.target, self.timesince())
        if self.action_object:
            return u'%s %s %s %s %s ago' % (self.actor, self.verb, self.action_object, self.timesince())
        return u'%s %s %s ago' % (self.actor, self.verb, self.timesince())

    def actor_url(self):
        """
        Returns the URL to the ``actstream_actor`` view for the current actor
        """
        return reverse('actstream_actor', None,
                       (self.actor_content_type.pk, self.actor_object_id))

    def target_url(self):
        """
        Returns the URL to the ``actstream_actor`` view for the current target
        """
        return reverse('actstream_actor', None,
                       (self.target_content_type.pk, self.target_object_id))

    def action_object_url(self):
        """
        Returns the URL to the ``actstream_actor`` view for the current action object
        """
        return reverse('actstream_actor', None,
            (self.action_object_content_type.pk, self.action_object_object_id))

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the current timestamp
        """
        from django.utils.timesince import timesince as timesince_
        return timesince_(self.timestamp, now)

    @models.permalink
    def get_absolute_url(self):
        return ('actstream.views.detail', [self.pk])


# convenience accessors
actor_stream = Action.objects.actor
action_object_stream = Action.objects.action_object
target_stream = Action.objects.target
model_stream = Action.objects.model_actions


def action_handler(verb, **kwargs):
    """
    Handler function to create Action instance upon action signal call.
    
    """
    kwargs.pop('signal', None)
    actor = kwargs.pop('sender')
    actor_ct = ContentType.objects.get_for_model(actor)
    newaction = Action(actor_content_type=actor_ct,
                    actor_object_id=actor.pk,
                    verb=unicode(verb),
                    public=bool(kwargs.pop('public', True)),
                    description=kwargs.pop('description', None),
                    timestamp=kwargs.pop('timestamp', datetime.now()))

    for opt in ('target', 'action_object'):
        obj = kwargs.pop(opt, None)
        if not obj is None:
            setattr(newaction, '%s_object_id' % opt, obj.pk)
            setattr(newaction, '%s_content_type' % opt,
                    ContentType.objects.get_for_model(obj))

    newaction.save()


action.connect(action_handler, sender=None, dispatch_uid='actstream.models')
