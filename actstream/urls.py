from django.conf.urls.defaults import *
from actstream import feeds

urlpatterns = patterns('actstream.views',
    # Syndication Feeds
    url(r'^feed/(?P<content_type_id>\d+)/(?P<object_id>\d+)/atom/$', 
        feeds.AtomObjectActivityFeed(), 
        name='actstream_object_feed_atom'),
    url(r'^feed/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$', 
        feeds.ObjectActivityFeed(), 
        name='actstream_object_feed'),
    url(r'^feed/(?P<content_type_id>\d+)/atom/$', 
        feeds.AtomModelActivityFeed(), 
        name='actstream_model_feed_atom'),
    url(r'^feed/(?P<content_type_id>\d+)/(?P<object_id>\d+)/as/$', 
        feeds.ActivityStreamsObjectActivityFeed(), 
        name='actstream_object_feed_as'),
    url(r'^feed/(?P<content_type_id>\d+)/$', feeds.ModelActivityFeed(), 
        name='actstream_model_feed'),
    url(r'^feed/$', feeds.UserActivityFeed(), 
        name='actstream_feed'),
    url(r'^feed/atom/$', feeds.AtomUserActivityFeed(), 
        name='actstream_feed_atom'),

    # Actor lists
    url(r'^actors/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$', 'actor', 
        name='actstream_actor'),
    url(r'^actors/(?P<content_type_id>\d+)/$', 'model', 
        name='actstream_model'),

    url(r'^detail/(?P<action_id>\d+)/$', 'detail', 
        name='actstream_detail'),
    url(r'^(?P<username>[-\w]+)/$', 'user', 
        name='actstream_user'),
    url(r'^$', 'stream', 
        name='actstream'),
)
