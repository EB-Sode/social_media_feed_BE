# apps/users/types.py
import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model

User = get_user_model()

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email", "bio", "profile_image", "created_at", "location", "birth_date", "cover_image")

    followers_count = graphene.Int()
    following_count = graphene.Int()
    posts_count = graphene.Int()
    
    def resolve_followers_count(self, info):
        return self.followers_count()
    
    def resolve_following_count(self, info):
        return self.following_count()
    
    def resolve_posts_count(self, info):
        return self.posts.count()

        
