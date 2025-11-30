import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "social_media_feed.settings_test")

import django
django.setup()
import pytest


@pytest.fixture
def api_client():
    """GraphQL API client."""
    from django.test import Client
    return Client()


@pytest.fixture
def user_factory(db):
    """Factory for creating test users."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    def create_user(username="testuser", email="test@example.com", password="testpass123", **kwargs):
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **kwargs
        )
    return create_user


@pytest.fixture
def user(user_factory):
    """Create a single test user."""
    return user_factory()


@pytest.fixture
def other_user(user_factory):
    """Create another test user."""
    return user_factory(username="otheruser", email="other@example.com")


@pytest.fixture
def authenticated_client(api_client, user):
    from rest_framework_simplejwt.tokens import RefreshToken
    """GraphQL client with JWT authentication."""
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    api_client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
    return api_client


@pytest.fixture
def post_factory(db):
    from apps.posts.models import Post
    """Factory for creating test posts."""
    def create_post(author, content="Test post content", **kwargs):
        return Post.objects.create(
            author=author,
            content=content,
            **kwargs
        )
    return create_post


@pytest.fixture
def post(user, post_factory):
    """Create a single test post."""
    return post_factory(author=user)


@pytest.fixture
def comment_factory(db):
    from apps.posts.models import Comment
    """Factory for creating test comments."""
    def create_comment(post, author, content="Test comment", **kwargs):
        return Comment.objects.create(
            post=post,
            author=author,
            content=content,
            **kwargs
        )
    return create_comment


@pytest.fixture
def follow_factory(db):
    from apps.follows.models import Follow
    """Factory for creating follow relationships."""
    def create_follow(follower, followed):
        return Follow.objects.create(
            follower=follower,
            followed=followed
        )
    return create_follow