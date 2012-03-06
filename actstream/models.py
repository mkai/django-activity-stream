from datetime import datetime
from django.db import models
from django.db.models import Q
from django.utils.timesince import timesince as timesince_
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from actstream.signals import action
from annoying.fields import JSONField


class ActionManager(models.Manager):
    """
    Default manager for actions.
    
    """
    def public(self, *args, **kwargs):
        """
        Only return public actions
        
        """
        kwargs['public'] = True
        return self.filter(*args, **kwargs)

    def actor(self, object, **kwargs):
        """
        Stream of most recent actions where object is the actor.
        Keyword arguments will be passed to Action.objects.filter
        
        """
        return self.filter(actor_object_id=object.pk,
            actor_content_type=ContentType.objects.get_for_model(object))

    def target(self, object, **kwargs):
        """
        Stream of most recent actions where object is the target.
        Keyword arguments will be passed to Action.objects.filter
        
        """
        return self.filter(target_object_id=object.pk,
            target_content_type=ContentType.objects.get_for_model(object))

    def action_object(self, object, **kwargs):
        """
        Stream of most recent actions where object is the action_object.
        Keyword arguments will be passed to Action.objects.filter
        
        """
        ct = ContentType.objects.get_for_model(object)
        return self.filter(action_object_object_id=object.pk,
            action_object_content_type=ct)

    def for_model(self, model, **kwargs):
        """
        Stream of most recent actions by any particular model
        
        """
        ctype = ContentType.objects.get_for_model(model)
        return self.public(Q(target_content_type=ctype) \
            | Q(action_object_content_type=ctype) \
            | Q(actor_content_type=ctype)
        )


##############
### Models ###
##############
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
    verb = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=datetime.now)
    public = models.BooleanField(default=True)
    extra_data = JSONField(blank=True, null=True)

    actor_content_type = models.ForeignKey(ContentType, related_name='actor')
    actor_object_id = models.CharField(max_length=255)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')

    target_content_type = models.ForeignKey(ContentType, related_name='target',
        blank=True, null=True)
    target_object_id = models.CharField(max_length=255, blank=True, null=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    action_object_content_type = models.ForeignKey(ContentType, 
        related_name='action_object', blank=True, null=True)
    action_object_object_id = models.CharField(max_length=255, blank=True, 
        null=True)
    action_object = GenericForeignKey('action_object_content_type', 
        'action_object_object_id')

    objects = ActionManager()

    class Meta:
        ordering = ('-timestamp',)

    def __unicode__(self):
        if self.target:
            if self.action_object:
                return u'%s %s %s on %s %s ago' % (self.actor, self.verb, self.action_object, self.target, self.timesince())
            else:
                return u'%s %s %s %s ago' % (self.actor, self.verb, self.target, self.timesince())
        if self.action_object:
            return u'%s %s %s %s ago' % (self.actor, self.verb, self.action_object, self.timesince())
        return u'%s %s %s ago' % (self.actor, self.verb, self.timesince())

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        
        """
        return timesince_(self.timestamp, now)


def on_action_sent(verb, **kwargs):
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
                    timestamp=kwargs.pop('timestamp', datetime.now()),
                    extra_data=kwargs.pop('extra_data', ''))

    for opt in ('target', 'action_object'):
        obj = kwargs.pop(opt, None)
        if not obj is None:
            setattr(newaction, '%s_object_id' % opt, obj.pk)
            setattr(newaction, '%s_content_type' % opt,
                    ContentType.objects.get_for_model(obj))

    newaction.save()

action.connect(on_action_sent, sender=None, dispatch_uid='actstream.models')
