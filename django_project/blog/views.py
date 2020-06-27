from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Like
from django.http import HttpResponseRedirect
from django.contrib import messages
from users.models import Profile
from django.db.models import Count, Sum, Q
from django.core.paginator import Paginator

	
def home(request):
	context = {
	'posts' : Post.objects.all()
	}
	return render(request, 'blog/home.html', context)

class PostListView(LoginRequiredMixin, ListView):
	model = Post
	template_name = 'blog/home.html'
	context_object_name = 'posts'
	# ordering = ['-date_posted']
	paginate_by = 5

	def get_queryset(self):
		username=self.request.user
		return Post.objects.exclude(author=username).order_by('-date_posted')

class UserPostListView(LoginRequiredMixin, ListView):
    context_object_name = 'posts'    
    template_name = 'blog/user_posts.html'
    paginate_by = 5

    def get_queryset(self):
    	user = get_object_or_404(User, username=self.kwargs.get('username'))
    	return Post.objects.filter(author=user).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super(UserPostListView, self).get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['following'] = Profile.objects.filter(followed=user)
        context['profile_likes'] = Post.objects.filter(author=user).annotate(like_count=Count('liked')).aggregate(total_likes=Sum('like_count'))['total_likes']
        return context


class PostDetailView(LoginRequiredMixin, DetailView):
	model = Post
		

class PostCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
	model = Post
	fields = ['title', 'content']
	success_message = "Your blog has been posted sucessfully!"

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
	model = Post
	fields = ['title', 'content']
	success_message = "Your post has been updated sucessfully!"

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)

	def test_func(self):
		post = self.get_object()
		if self.request.user == post.author:
			return True
		return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Post
	success_url = '/user-profile/'

	def test_func(self):
		post = self.get_object()
		if self.request.user == post.author:
			return True
		return False

	def delete(self, request, *args, **kwargs):
	    response = super().delete(request, *args, **kwargs)
	    messages.success(self.request, 'Your post has been deleted sucessfully!')
	    return response
		

def about(request):
	return render(request, 'blog/about.html', {'title':'About'})


def like_post(request):
	user = request.user
	if request.method == 'POST':
		post_id = request.POST.get('post_id')
		post_obj = Post.objects.get(id=post_id)

		if user in post_obj.liked.all():
			post_obj.liked.remove(user)
		else:
			post_obj.liked.add(user)

		like, created = Like.objects.get_or_create(user=user, post_id=post_id)

		if not created:
			if like.value == 'Like':
				like.value = 'Unlike'
			else:
				like.value = 'Like'

		like.save()
	return redirect(request.META.get('HTTP_REFERER', 'blog-home'))


def search(request):
	query = request.GET.get('user_search_input')

	if query:
		results = Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
	else:
		return HttpResponse("Access denied")
	context={
	'results' : results,
	'search_word' : query
	}
	return render(request, 'blog/search.html', context)