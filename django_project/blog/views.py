from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .forms import CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Like, Comment
from django.contrib import messages
from users.models import Profile
from django.db.models import Count, Sum, Q, Min, Max, Avg
from django import template
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
	
@login_required
def post_detail(request, pk):

	object = Post.objects.get(id=pk)
	comments = Comment.objects.filter(post=pk, reply=None).order_by('-date_posted')
	is_bookmark = False
	if object.bookmark.filter(id=request.user.id).exists():
		is_bookmark=True

	if request.method == 'POST':
		comment_form = CommentForm(request.POST or None)
		if comment_form.is_valid():
			comment = request.POST.get('comment')
			reply_id = request.POST.get('comment_id')
			comment_obj=None
			if reply_id:
				comment_obj=Comment.objects.get(id=reply_id)
			content = Comment.objects.create(post=object, user=request.user, comment=comment, reply=comment_obj)
			content.save()
			messages.success(request, f'Your comment has been posted!')
			return HttpResponseRedirect(object.get_absolute_url())

	else:
		comment_form=CommentForm()

	context = {
	'object' : object,
	'comments': comments,
	'comment_form': comment_form,
	'is_bookmark': is_bookmark
	}
	return render(request, 'blog/post_detail.html', context)

@login_required
def post_detail_likes(request, pk):
	context = {
	'object' : Post.objects.get(id=pk),
	}
	return render(request, 'blog/post_detail_likes.html', context)

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
        context['profile_info'] = Profile.objects.get(user=user)
        context['profile_likes'] = Post.objects.filter(author=user).annotate(like_count=Count('liked')).aggregate(total_likes=Sum('like_count'))['total_likes']
        return context

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

@login_required
def like_post(request):
	user = request.user
	post_id = request.POST.get('id')
	post_obj = get_object_or_404(Post, id=post_id)

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
	if request.is_ajax():
	    html = render_to_string('blog/like_section.html', request=request)
	    return JsonResponse({'form': html})

@login_required
def search(request):
	query = request.GET.get('user_search_input')

	if query:
		results = Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query)).order_by('-date_posted')
	else:
		return HttpResponse("Access denied")
	context={
	'results' : results,
	'search_word' : query
	}
	return render(request, 'blog/search.html', context)

@login_required
def most_liked_posts(request):
	query = Like.objects.filter(value='Like').values('value', 'post_id').order_by().annotate(like_count=Count('post_id'))
	maxval = sorted(query, key=lambda x:x['like_count'], reverse=True)[:5]
	posts = Post.objects.all()
	context={
	'maxval':maxval,
	'posts': posts
	}
	return render(request, 'blog/most_liked_posts.html', context)

@login_required
def most_liked_authors(request):
	query = Like.objects.filter(value='Like').values('post__author').order_by().annotate(profile_like_count=Count('post__author'))
	maxval = sorted(query, key=lambda x:x['profile_like_count'], reverse=True)[:5]
	users = User.objects.all()
	context={
	'maxval':maxval,
	'users': users
	}
	return render(request, 'blog/most_liked_authors.html', context)
@login_required
def bookmark_post(request, pk):
	post = get_object_or_404(Post, id=pk)
	if post.bookmark.filter(id=request.user.id).exists():
		post.bookmark.remove(request.user)
		messages.success(request, f'Removed from bookmark successfully!')
	else:
		post.bookmark.add(request.user)
		messages.success(request, f'Added to bookmark successfully!')
	return HttpResponseRedirect(post.get_absolute_url())
@login_required
def my_bookmarks(request):
	user = request.user
	bookmarks_qs = user.bookmark.all()
	bookmarks = list(reversed(bookmarks_qs))

	context={
	'bookmarks': bookmarks
	}

	return render (request, 'blog/my_bookmarks.html', context)