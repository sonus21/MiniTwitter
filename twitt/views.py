from django.contrib.auth import logout
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.generic import TemplateView, CreateView, FormView, UpdateView
import redis

from .models import Twit, Follow
from twitt.forms import SignUpForm, TwitForm


class LoginRequiredMixin(object):
	"""
	It ensures that use is authenticated
	"""
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class HomeView(LoginRequiredMixin, TemplateView):
	"""
	Home page login is required if not then request
	"""
	template_name = 'index.html'
	def get_context_data(self, **kwargs):
		conn = redis.StrictRedis(host='localhost', port=6379, db=0)

		# displaying only first 10 twits
		# Using AJAX it can be used for further twits
		twit_list = conn.lrange(self.request.user.pk, start=0, end=10)

		twits = []
		for twit in twit_list:
			tp = twit.split('|')
			tp[1] = tp[1].split('.')[0]
			twits.append(tp)
		return {'title': 'Welcome Simple Twitter', 'twits': twits, 'post_form':TwitForm}


class FollowUserView(LoginRequiredMixin, CreateView):
	"""
	Follow a user
	1. get returns list of users
	2. post follows a user
	"""
	def get(self, request, *args, **kwargs):
		following_list = list(Follow.objects.filter(follower=request.user).values_list('following').values_list('pk',
		                                                                                                        flat=True))
		following_list.append(request.user.pk)
		users = User.objects.exclude(pk__in=following_list)
		return TemplateResponse(request, 'follow.html', {'user_list':users})

	def post(self, request, *args, **kwargs):
		user = get_object_or_404(User, pk=request.POST.get('pk'))

		# Direct follow  no notification etc
		# Here AJAX request can be used to optimize the db query

		Follow(follower=request.user, following=user).save()

		#redirect to home page
		return redirect('/')


class AccountProfileView(TemplateView):
	template_name = 'account_profile.html'

	def get(self, request, *args, **kwargs):
		context = dict()
		context['user'] = request.user
		return TemplateResponse(request, self.template_name, context)




class FollowListView(LoginRequiredMixin, TemplateView):
	template_name = "following.html"
	"""
	List of the user that I am following
	"""

	def get_context_data(self, **kwargs):
		followings = Follow.objects.filter(follower=self.request.user).values_list('following', flat=True)
		followings = User.objects.filter(pk__in=followings)
		return {'following_list': followings}


class MyTwitsView(LoginRequiredMixin, TemplateView):
	template_name = 'my_twits.html'
	"""
	Display all twits made by me
	"""
	def get_context_data(self, **kwargs):
		return {'twit_list':Twit.objects.filter(author=self.request.user)}


class SignUpView(FormView):
	template_name = 'registration/signup.html'
	"""
	Signup a user
	"""

	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated():
			return redirect('/')
		form = SignUpForm()
		return TemplateResponse(request, self.template_name, {'form':form})


	def post(self, request, *args, **kwargs):
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('login')
		return TemplateResponse(request, self.template_name, {'form':form})


class PostTwitView(LoginRequiredMixin, FormView):

	"""
	GET method is not allowed so 404
	"""
	def get(self, request, *args, **kwargs):
		raise Http404

	def post(self, request, *args, **kwargs):
		twit_form = TwitForm(request.POST)
		if twit_form.is_valid():
			twit_form.instance.author = request.user
			twit_form.save()

			# currently we have use separator as pipe and no partitioning of list is done
			conn = redis.StrictRedis(host='localhost', port=6379, db=0)
			followings = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
			msg = "%s|%s|%s" % (request.user, now(),twit_form.cleaned_data['content'])
			for fol in followings:
				conn.lpush(fol, msg)
		else:
			print(twit_form.errors)
		return redirect('/')


class EditTwitView(LoginRequiredMixin, UpdateView):
	template_name = 'edit_twit.html'
	"""
	Edit a twit
	"""

	def get(self, request, *args, **kwargs):
		twit = self.get_twit(request, **kwargs)
		if isinstance(twit, HttpResponse):
			return twit
		form = TwitForm(instance=twit)
		return TemplateResponse(request,self.template_name, {'form': form})


	def post(self, request, *args, **kwargs):
		twit = self.get_twit(request, **kwargs)
		if isinstance(twit, HttpResponse):
			return twit

		form = TwitForm(request.POST, instance=twit)
		if form.is_valid():
			form.save()
			return redirect('/')

		return TemplateResponse(request,self.template_name, {'form': form})

	def get_twit(self,request, **kwargs):
		pk = kwargs.get('pk')
		twit = get_object_or_404(Twit, pk=pk)
		"""
		User is authenticated and twit belongs to requested user.
		"""
		if twit.author != request.user:
			return redirect('/')
		return twit


def custom_logout(request):
	"""
	:param request:
	:return: redirect to home page
	"""
	logout(request)
	return redirect('/')