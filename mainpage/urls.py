from django.conf.urls.defaults import *
from mainpage.views import main_page, market_put, view_detail, populate, add_comment, add_favourite

urlpatterns = patterns('',
    (r'^$', main_page),
    (r'^stubmaker/$', market_put),
    (r'^populate/$', populate),
    (r'^detail/(?P<market_id>\d+)/$', view_detail),
    (r'^comment/$', add_comment),
    (r'^add_to_favourite/$', add_favourite)
)