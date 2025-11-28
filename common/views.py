from graphene_django.views import GraphQLView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class AuthenticatedGraphQLView(GraphQLView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        jwt_auth = JWTAuthentication()

        try:
            # Try to authenticate user via Simple JWT
            user_auth_tuple = jwt_auth.authenticate(request)
            if user_auth_tuple:
                request.user = user_auth_tuple[0]
            else:
                request.user = AnonymousUser()
        except:
            request.user = AnonymousUser()

        return super().dispatch(request, *args, **kwargs)
