from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from actstream.gfk import GFKManager
from actstream.decorators import stream


class ActionManager(GFKManager):
    """
    Default manager for Actions, accessed through Action.objects
    
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
