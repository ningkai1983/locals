from django.conf.urls.defaults import *
from main.requestHandlers import *
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Impressions.views.home', name='home'),
    # url(r'^Impressions/', include('Impressions.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    (r'^privacy', 'main.views.privacy'),
    (r'^heartBeat', 'main.views.heartBeat'),
    (r'^simpleTest', 'main.views.test'),
    (r'^register', Register.as_view()),
    (r'^upload', postImage.as_view()),
    (r'^login', LoginView.as_view()),
    (r'^getAround', getAround.as_view()),
    
)
