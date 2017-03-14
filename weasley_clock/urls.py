"""weasley_clock URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
1. Add an import:  from my_app import views
2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
1. Add an import:  from other_app.views import Home
2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
1. Import the include() function: from django.conf.urls import url, include
2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url
from django.contrib import admin
from clock import views

urlpatterns = [
	# Admin
	url(r'^admin/', admin.site.urls),
	# Web Pages
	url(r'^$', views.index, name='index'),
	url(r'clock/(?P<clock_id>[0-9]+)/$', views.clock_view, name='clock view'),
	url(r'create-clock/$', views.create_clock_form, name='create clock form'),
	# Authentification
	url(r'^sign-in', views.login_user, name='login user'),
	url(r'^log-out', views.logout_user, name='logout user'),
	# CRUD
	url(r'^update-location/$', views.update_location, name='update location'),
	url(r'create-clock-object/$', views.create_clock_object, name='create clock object'),
	url(r'^clock/(?P<clock_id>[0-9]+)/states/$', views.get_states_from_clock_id, name='get states for clock'),
	url(r'^clock/(?P<clock_id>[0-9]+)/current-states/$', views.get_current_states_from_clock_id, name='get states for clock'),
	url(r'^clock/(?P<clock_id>[0-9]+)/manage-states/$', views.manage_states, name='manage states'),
	# url(r'^clock/(?P<clock_id>[0-9]+)/manage-states-post/$', views.manage_states_post, name='manage states post')
	url(r'^clock/manage-states-post/$', views.manage_states_post, name='manage states post')
]
