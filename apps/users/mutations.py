# mutations.py
import graphene
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .types import UserType
from graphql import GraphQLError
from graphene_file_upload.scalars import Upload
from .models import UserImage

User = get_user_model()


class SignUpMutation(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        bio = graphene.String()

    user = graphene.Field(UserType)
    token = graphene.String()
    refresh_token = graphene.String()

    def mutate(self, info, username, email, password, bio=None):
        # Check if user exists
        if User.objects.filter(username=username).exists():
            raise Exception("Username already exists")
        
        if User.objects.filter(email=email).exists():
            raise Exception("Email already exists")
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            bio=bio or ""
        )
        
        # Generate tokens using rest_framework_simplejwt
        refresh = RefreshToken.for_user(user)
        
        return SignUpMutation(
            user=user,
            token=str(refresh.access_token),
            refresh_token=str(refresh)
        )


class LoginMutation(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)
    token = graphene.String()
    refresh_token = graphene.String()

    def mutate(self, info, username, password):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Exception("Invalid credentials")
        
        if not user.check_password(password):
            raise Exception("Invalid credentials")
        
        # Generate tokens using rest_framework_simplejwt
        refresh = RefreshToken.for_user(user)
        
        return LoginMutation(
            user=user,
            token=str(refresh.access_token),  # This will have 'exp' claim
            refresh_token=str(refresh)
        )

class RefreshTokenMutation(graphene.Mutation):
    class Arguments:
        refresh_token = graphene.String(required=True)

    token = graphene.String()
    refresh_token = graphene.String()

    def mutate(self, info, refresh_token):
        try:
            # Create refresh token object
            refresh = RefreshToken(refresh_token)
            
            # Generate new access token
            new_access_token = str(refresh.access_token)
            
            # If ROTATE_REFRESH_TOKENS is True, this generates a new refresh token
            if hasattr(refresh, 'set_jti'):
                refresh.set_jti()
                refresh.set_exp()
                new_refresh_token = str(refresh)
            else:
                new_refresh_token = refresh_token
            
            return RefreshTokenMutation(
                token=new_access_token,
                refresh_token=new_refresh_token
            )
        except TokenError as e:
            raise Exception(f"Invalid or expired refresh token: {str(e)}")


class UpdateProfileMutation(graphene.Mutation):
    class Arguments:
        bio = graphene.String()
        email = graphene.String()
        profile_image = graphene.String()  # URL or base64
        location = graphene.String() 

    user = graphene.Field(UserType)

    def mutate(self, info, bio=None, location=None, email=None, profile_image=None):
        user = info.context.user
        
        if not user.is_authenticated:
            raise Exception("Authentication required")
        
        if bio is not None:
            user.bio = bio

        user.email = email
        if location is not None:
            user.location = location 
        
        if email is not None:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                raise Exception("Email already in use")
            user.email = email
        
        if profile_image is not None:
            user.profile_image = profile_image
        
        user.save()
        return UpdateProfileMutation(user=user)
    
class UpdateUserImages(graphene.Mutation):
    class Arguments:
        profile = Upload(required=False)
        cover = Upload(required=False)

    success = graphene.Boolean()
    message = graphene.String()
    profile_image = graphene.String()
    cover_image = graphene.String()

    def mutate(self, info, profile=None, cover=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        if profile:
            obj = UserImage.objects.create(kind="profile", file=profile)
            # save relative path like "user_images/xxx.jpg"
            user.profile_image = obj.file.name

        if cover:
            obj = UserImage.objects.create(kind="cover", file=cover)
            user.cover_image = obj.file.name

        user.save()
        return UpdateUserImages(
            success=True,
            message="Updated successfully",
            profile_image=user.profile_image,
            cover_image=user.cover_image,
        )


class LogoutMutation(graphene.Mutation):
    class Arguments:
        refresh_token = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, refresh_token):
        try:
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
            return LogoutMutation(success=True)
        except TokenError:
            raise Exception("Invalid or expired refresh token")
        
class DeleteAllUsersMutation(graphene.Mutation):
    success = graphene.Boolean()
    deleted_count = graphene.Int()

    @classmethod
    def mutate(cls, root, info):
        user = info.context.user

        # 🔒 Security check
        if user.is_anonymous or not user.is_superuser:
            raise GraphQLError("Not authorized")

        deleted_count, _ = User.objects.all().delete()

        return DeleteAllUsersMutation(
            success=True,
            deleted_count=deleted_count
        )
