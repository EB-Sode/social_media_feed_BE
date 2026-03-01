import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType

from apps.posts.models import Post
from apps.search.models import Hashtag

User = get_user_model()


class SearchUserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "profile_image", "bio")


class SearchPostType(DjangoObjectType):
    image_url = graphene.String()
    class Meta:
        model = Post
        fields = ("id", "content", "image", "created_at", "author")

    def resolve_image_url(self, info):
        return self.image


class SearchHashtagType(DjangoObjectType):
    class Meta:
        model = Hashtag
        fields = ("id", "name")


class SearchResultsType(graphene.ObjectType):
    users = graphene.List(SearchUserType)
    posts = graphene.List(SearchPostType)
    hashtags = graphene.List(SearchHashtagType)


class SearchQuery(graphene.ObjectType):
    search = graphene.Field(
        SearchResultsType,
        q=graphene.String(required=True),
        type=graphene.String(required=False),
        limit=graphene.Int(required=False, default_value=10),
    )

    def resolve_search(self, info, q, type=None, limit=10):
        q = q.strip()
        if not q:
            return SearchResultsType(users=[], posts=[], hashtags=[])

        users_qs = User.objects.none()
        posts_qs = Post.objects.none()
        hashtags_qs = Hashtag.objects.none()

        if type in (None, "all", "users"):
            users_qs = User.objects.filter(username__icontains=q)[:limit]

        if type in (None, "all", "posts"):
            posts_qs = Post.objects.filter(content__icontains=q).select_related("author")[:limit]

        if type in (None, "all", "hashtags"):
            hashtags_qs = Hashtag.objects.filter(name__icontains=q)[:limit]

        return SearchResultsType(
            users=list(users_qs),
            posts=list(posts_qs),
            hashtags=list(hashtags_qs),
        )