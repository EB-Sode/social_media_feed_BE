import graphene
from django.apps import AppConfig
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
from apps.posts.models import Post
from apps.search.models import Hashtag
User = get_user_model()
from .types import SearchUserType, SearchResultsType


class SearchQuery(graphene.ObjectType):
    search = graphene.Field(
        SearchResultsType,
        q=graphene.String(required=True),
        type=graphene.String(required=False, default_value="all"),
        limit=graphene.Int(required=False, default_value=10),
    )

    def resolve_search(self, info, q, type="all", limit=10):
        q = (q or "").strip()
        if not q:
            return SearchResultsType(users=[], posts=[], hashtags=[])

        users = []
        posts = []
        hashtags = []

        # USERS
        if type in ("all", "users"):
            users_qs = User.objects.filter(username__icontains=q)[:limit]
            users = [
                SearchUserType(
                    id=u.id,
                    username=u.username,
                    profile_image=getattr(u, "profile_image", None),
                    bio=getattr(u, "bio", None),
                )
                for u in users_qs
            ]

        # POSTS
        if type in ("all", "posts"):
            posts = list(
                Post.objects.filter(content__icontains=q)
                .select_related("author")[:limit]
            )

        # HASHTAGS
        if type in ("all", "hashtags"):
            hashtags = list(Hashtag.objects.filter(name__icontains=q)[:limit])

        return SearchResultsType(users=users, posts=posts, hashtags=hashtags)