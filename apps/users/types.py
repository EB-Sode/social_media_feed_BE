# apps/users/types.py
import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model

User = get_user_model()

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email", "bio", "profile_image", "created_at", "location", "birth_date", "cover_image")

        
