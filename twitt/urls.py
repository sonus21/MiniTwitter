"""""""""""""""""""""""""""""""""""""""""
# @author  sonus
# @date 02 - Apr - 2016
# @copyright sonus
# GitHub http://github.com/sonus21
"""""""""""""""""""""""""""""""""""""""""

from django.conf.urls import url, include

from .views import SignUpView, FollowUserView, custom_logout, AccountProfileView,\
	PostTwitView, FollowListView, EditTwitView, HomeView, MyTwitsView

from django.contrib.auth.views import *

urlpatterns = [

	url(r'^$', HomeView.as_view(), name='home'),

	url(r'^accounts/profile/?$', AccountProfileView.as_view(), name='profile'),
	url(r'^accounts/login/?$', login, name='login'),
	url(r'^accounts/signup/?$', SignUpView.as_view(), name='signup'),
	url(r'^accounts/logout/?$', custom_logout, name='logout'),

	url('^accounts/twit/?$', MyTwitsView.as_view(), name='my_twits'),

	url('^post/twit/?$', PostTwitView.as_view(), name='post_twit'),
	url('^following/?$', FollowListView.as_view(), name='following_list'),
	url('^edit/twit/(?P<pk>[0-9]+)/?$', EditTwitView.as_view(), name='edit_twit'),

	url('^search/user/?$', FollowUserView.as_view(), name='follow_user'),
	url('^search/twit/', include('haystack.urls')),
]
