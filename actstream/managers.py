from functools import wraps
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType


def stream(func):
    """
    Stream decorator to be applied to methods of an ``ActionManager`` subclass

    Syntax::

        from actstream.decorators import stream
        from actstream.managers import ActionManager

        class MyManager(ActionManager):
            @stream
            def foobar(self, ...):
                ...

    """
    @wraps(func)
    def wrapped(manager, *args, **kwargs):
        offset, limit = kwargs.pop('_offset', None), kwargs.pop('_limit', None)
        qs = func(manager, *args, **kwargs)[offset:limit]
        return qs
    return wrapped


class ActionManager(models.Manager):
    """
    Default manager for Actions.
    
    """
    def public(self, *args, **kwargs):
        """
        Only return public actions
        
        """
        kwargs['public'] = True
        return self.filter(*args, **kwargs)

    @stream
    def actor(self, object, **kwargs):
        """
        Stream of most recent actions where object is the actor.
        Keyword arguments will be passed to Action.objects.filter
        
        """
        return self.filter(actor_object_id=object.pk,
            actor_content_type=ContentType.objects.get_for_model(object))

    @stream
    def target(self, object, **kwargs):
        """
        Stream of most recent actions where object is the target.
        Keyword arguments will be passed to Action.objects.filter
        
        """
        return self.filter(target_object_id=object.pk,
            target_content_type=ContentType.objects.get_for_model(object))

    @stream
    def action_object(self, object, **kwargs):
        """
        Stream of most recent actions where object is the action_object.
        Keyword arguments will be passed to Action.objects.filter
        
        """
        ct = ContentType.objects.get_for_model(object)
        return self.filter(action_object_object_id=object.pk,
            action_object_content_type=ct)

    @stream
    def model_actions(self, model, **kwargs):
        """
        Stream of most recent actions by any particular model
        
        """
        ctype = ContentType.objects.get_for_model(model)
        return self.public(Q(target_content_type=ctype) \
            | Q(action_object_content_type=ctype) \
            | Q(actor_content_type=ctype)
        )
