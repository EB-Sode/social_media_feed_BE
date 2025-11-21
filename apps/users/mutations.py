# apps/users/mutations.py
"""
User mutations: Signup, Login (JWT example), UpdateProfile.

Notes for junior dev:
 - Signup creates a user and returns the user object.
 - Login returns a token (this example uses PyJWT — you can replace it with
   any JWT library or Django library you prefer).
 - UpdateProfile shows updating fields and saving the user.
"""

import graphene
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
import jwt
from graphene_file_upload.scalars import Upload  # if you want to support file uploads

User = get_user_model()


class SignUpMutation(graphene.Mutation):
    """
    Create a new user. Real projects require email validation, password strength check, etc.
    """
    user = graphene.Field(lambda: graphene.NonNull(lambda: UserType))

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        bio = graphene.String(required=False)
        profile_image = Upload(required=False)  # optional file upload

    def mutate(self, info, username, email, password, bio=None, profile_image=None):
        # Basic creation flow; add validations as needed
        user = User(username=username, email=email)
        user.set_password(password)
        if bio:
            user.bio = bio
        if profile_image:
            user.profile_image = profile_image
        user.save()
        return SignUpMutation(user=user)


class LoginMutation(graphene.Mutation):
    """
    Basic login mutation returning a JWT token.
    Requires PyJWT (pip install PyJWT).
    For production: add token expiry, refresh tokens, and revocation strategy.
    """
    token = graphene.String()
    user = graphene.Field(lambda: graphene.NonNull(lambda: UserType))

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, password):
        # Use Django's authenticate helper
        user = authenticate(username=username, password=password)
        if user is None:
            raise Exception("Invalid username or password")

        # Example: Simple JWT token (no refresh, no claims beyond user id)
        payload = {"user_id": user.id}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        # On PyJWT >= 2.0 token is bytes; ensure str
        if isinstance(token, bytes):
            token = token.decode("utf-8")

        return LoginMutation(token=token, user=user)


class UpdateProfileMutation(graphene.Mutation):
    """
    Allow the authenticated user to update their own profile.
    """
    user = graphene.Field(lambda: graphene.NonNull(lambda: UserType))

    class Arguments:
        username = graphene.String(required=False)
        bio = graphene.String(required=False)
        profile_image = Upload(required=False)

    def mutate(self, info, username=None, bio=None, profile_image=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        if username:
            user.username = username
        if bio is not None:
            user.bio = bio
        if profile_image is not None:
            user.profile_image = profile_image
        user.save()
        return UpdateProfileMutation(user=user)


# If using UserType in the same file, import it safely to avoid circular imports.
from .schema import UserType  # local import (safe because UserType is simple)
