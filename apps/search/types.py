import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType

from apps.posts.models import Post
from apps.search.models import Hashtag  # adjust if needed

User = get_user_model()


# ✅ Plain GraphQL object (NOT DjangoObjectType) to avoid registry conflicts
class SearchUserType(graphene.ObjectType):
    id = graphene.ID()
    username = graphene.String()
    profile_image = graphene.String()
    bio = graphene.String()


class SearchPostType(DjangoObjectType):
    image_url = graphene.String()

    class Meta:
        model = Post
        fields = ("id", "content", "image", "created_at", "author")

    def resolve_image_url(self, info):
        return self.image or None


class SearchHashtagType(DjangoObjectType):
    class Meta:
        model = Hashtag
        fields = ("id", "name")


class SearchResultsType(graphene.ObjectType):
    users = graphene.List(SearchUserType)
    posts = graphene.List(SearchPostType)
    hashtags = graphene.List(SearchHashtagType)
