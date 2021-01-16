from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


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
    post_list = group.group_posts.all()
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
    form = PostForm(request.POST or None)
    if form.is_valid():
        post_new = form.save(commit=False)
        post_new.author = request.user
        post_new.save()
        return redirect(reverse('posts:index'))
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    paginator = Paginator(author_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    follow = False
    if request.user.is_authenticated:
        if Follow.objects.filter(author=author, user=request.user).count() > 0:
            follow = True
    followers = Follow.objects.filter(author=author).count()
    following = Follow.objects.filter(user=author).count()

    context = {
        'author': author,
        'follow': follow,
        'followers': followers,
        'following': following,
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    author = post.author
    comments = Comment.objects.filter(post_id=post_id)
    form = CommentForm()
    context = {
        'author': author,
        'post': post,
        'form': form,
        'comments': comments,
        'dont_view_add_comment': True,
    }
    return render(request, 'detailed_post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if post.author != request.user:
        return redirect(reverse('posts:post',
                                kwargs={'username': username,
                                        'post_id': post_id}))
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.save()
        return redirect(reverse('posts:post',
                                kwargs={'username': username,
                                        'post_id': post_id}))
    return render(request, 'new_post.html', {'form': form,
                                             'edit': True,
                                             'post': post})


@login_required
def add_comment(request, username, post_id):
    post = Post.objects.get(id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect(reverse('posts:post', kwargs={'username': username,
                                                      'post_id': post_id}))
    return redirect(reverse('posts:post', kwargs={'username': username,
                                                  'post_id': post_id}))


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)

    return render(request, "follow.html", {
        'page': page,
        'paginator': paginator
    })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    count = Follow.objects.filter(user=request.user, author=author).count()
    if author != request.user and count == 0:
        Follow.objects.create(
            user=request.user,
            author=author,
        )
    return redirect(reverse('posts:profile', kwargs={'username': username}))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, user=request.user, author=author)
    follow.delete()
    return redirect(reverse('posts:profile', kwargs={'username': username}))
