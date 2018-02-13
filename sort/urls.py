from django.conf.urls import url

from . import views

app_name = 'sort'
urlpatterns = [
	url(r'^$', views.HomeSearch, name='home_search'),
	url(r'^analytics/$', views.AnalyticsView, name='analytics'),
	url(r'^sort_photos/$', views.HomePhotos, name='home_photos'),
	url(r'^sort_tags/$', views.HomeTags, name='home_tags'),
	url(r'^sort_photos/(?P<target_pk>[0-9]+)/$', views.SortPhotos, name='sort_photos'),
	url(r'^sort_tags/(?P<target_pk>[0-9]+)/$', views.SortTags, name='sort_tags')
]
