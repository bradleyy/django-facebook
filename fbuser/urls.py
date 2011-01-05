from django.conf.urls.defaults import *

urlpatterns = patterns('fbuser.views',
    (r'^fbreg/', 'fbreg', {}, 'fbreg'),
    (r'^fblink/', 'fblink', {}, 'fblink'),
)
