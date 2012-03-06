from django.dispatch import Signal

action = Signal(providing_args=['actor', 'verb', 'action_object', 
                                'target', 'timestamp', 'extra_data'])
