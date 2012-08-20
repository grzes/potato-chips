import logging
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import Http404

from chips.forms import SignupForm, PostForm
from chips.models import Blog, Post
from chips.users import require_user, fullurl


def postlist(request):
    """The blog view, if no user logged in or chosen display the home page."""
    # if no blog is selected invite the users to signup or redirect to dash
    if not request.blog:
        if request.user_blog:
            return redirect(fullurl(reverse('dash')))
        else:
            return render(request, "home.html")

    else:
        posts = Post.query_from(request.blog)
        return render(request, "blog.html", {
            'blog': request.blog,
            'posts': posts
        })


@require_user(with_blog=True)
def dash(request):
    """Users dashboard.

    It's like the main blog view but shows friend's posts."""

    if request.method == 'POST':
        form = PostForm(request.POST, blog=request.user_blog)
        if form.is_valid():
            form.save()
            return redirect(reverse('dash'))
    else:
        form = PostForm(blog=request.user_blog)

    posts = Post.query_for(reader=request.user_blog)

    return render(request, "dash.html", {
            'form': form,
            'blog': request.user_blog,
            'posts': posts
        })


@require_user(with_blog=False)
def signup(request):
    """Sets up a users's blog under a chosen name."""
    if request.user_blog:
        return redirect(reverse('dash')) # already have one

    if request.method == 'POST':
        form = SignupForm(request.POST, owner=request.user)
        if form.is_valid():
            return redirect(reverse('dash'))
    else:
        form = SignupForm(owner=request.user)

    return render(request, "signup.html", {
            'form': form
        })

@require_user(with_blog=True)
def follow(request, blog):
    """A form for confirming following a blog."""
    # This would ideally be a post from the original blog, but I can't figure out how to do
    # single sign on with the users api. If a custom django user backend was used we could
    # just se a wildcard domain for the auth coockies.
    blog = Blog.get_by_key_name(blog)
    if not blog:
        raise Http404

    if request.method == 'POST':
        # there's no form really, just post and pass the csrf check
        request.user_blog.follow(blog)
        return redirect(reverse('dash'))
    return render(request, "follow.html", {
        'follow_blog': blog,
        'is_following': request.user_blog.is_following(blog)
        })


def exception_test(request):
    logging.debug('Debug log')
    logging.warn('Warn log')
    logging.error('Error log')
    raise Exception()
