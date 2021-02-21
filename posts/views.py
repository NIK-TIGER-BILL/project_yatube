from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.select_related('group')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page,
         'paginator': paginator, }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {'group': group,
         'page': page,
         'paginator': paginator, }
    )


@login_required
def new_post(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'new_post.html', {'form': form})
    post_new = form.save(commit=False)
    post_new.author = request.user
    post_new.save()
    return redirect('posts:index')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    paginator = Paginator(author_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    follow = (request.user.is_authenticated and author != request.user
              and Follow.objects.filter(
                  author=author,
                  user=request.user).exists())
    context = {
        'author': author,
        'follow': follow,
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    author = post.author
    follow = (request.user.is_authenticated and author != request.user
              and Follow.objects.filter(
                  author=author,
                  user=request.user).exists())
    context = {
        'post': post,
        'form': form,
        'comments': comments,
        'author': author,
        'follow': follow
    }
    return render(request, 'detailed_post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if post.author != request.user:
        return redirect('posts:post', username=username, post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post', username=username, post_id=post_id)
    return render(request, 'new_post.html', {'form': form,
                                             'post': post})


@login_required
def add_comment(request, username, post_id):
    post = Post.objects.get(id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post', username=username, post_id=post_id)


def page_not_found(request, exception=None):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {
        'page': page,
        'paginator': paginator
    })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (author != request.user
        and not Follow.objects.filter(user=request.user,
                                      author=author).exists()):
        Follow.objects.create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(Follow, user=request.user,
                      author__username=username).delete()
    return redirect('posts:profile', username=username)
