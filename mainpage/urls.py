from django.conf.urls.defaults import *
from mainpage.views import main_page, market_put, view_detail, populate

urlpatterns = patterns('',
    (r'^$', main_page),
    (r'^stubmaker/$', market_put),
    (r'^populate/$', populate),
    (r'^detail/(?P<detail>\d+)/$', view_detail),
)