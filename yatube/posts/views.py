from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, Follow
from django.contrib.auth import get_user_model
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from .utils import paginator

User = get_user_model()


def index(request):
    """View функция главной страницы."""
    post_list = Post.objects.all()
    page_obj = paginator(post_list, request)
    context = {
        'page_obj': page_obj,
        'text': 'Главная страница',
        'index': "index"
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """View функция страницы группы."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginator(post_list, request)
    context = {
        'group': group,
        'page_obj': page_obj,
        'text': 'Страница группы',
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """View функция страницы профиля пользователя."""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = paginator(post_list, request)
    following = False
    if request.user.is_authenticated:
        following = author.following.filter(user=request.user).exists()
    context = {
        'author': author,
        'user': author,
        'page_obj': page_obj,
        'text': 'Страница группы',
        'post_count': post_list.count(),
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """View функция страницы поста по id."""
    post = get_object_or_404(
        Post.objects.select_related('group', 'author'), id=post_id
    )
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'post_count': post.author.posts.count(),
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """View функция формы создания нового поста."""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    context = {
        'form': form,
    }
    if request.method == 'POST':
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('posts:profile', request.user.username)
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """View функция формы редактирования поста."""
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'form': form,
        'is_edit': True
    }
    if post.author == request.user:
        if request.method == 'POST':
            if form.is_valid():
                new_post = form.save(commit=False)
                new_post.author = request.user
                new_post.save()
                return redirect('posts:post_detail', post_id)
        return render(request, 'posts/create_post.html', context)
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    """View функция создания нового комментария."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """View функция страницы подписок."""
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(post_list, request)
    context = {
        'page_obj': page_obj,
        'text': 'Главная страница',
        'follow': 'follow',
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """View функция создания подписки на автора."""
    author = get_object_or_404(User, username=username)
    user = request.user
    follow_exists = author.following.filter(user=user).exists()
    if author != user and not follow_exists:
        Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    """View функция удаления подписки на автора."""
    author = get_object_or_404(User, username=username)
    user = request.user
    follow = Follow.objects.filter(user=user, author=author)
    follow.delete()
    return redirect('posts:profile', username)
