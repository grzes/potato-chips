import logging
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from chips.forms import SignupForm, PostForm
from chips.models import Post
from chips.users import require_user


def postlist(request):
    """The blog view, if no user logged in or chosen display the home page."""
    return render(request, "home.html", {
            'blog': request.blog,
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


def exception_test(request):
    logging.debug('Debug log')
    logging.warn('Warn log')
    logging.error('Error log')
    raise Exception()
