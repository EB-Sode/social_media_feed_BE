# views.py
from graphene_django.views import GraphQLView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)


class AuthenticatedGraphQLView(GraphQLView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):

        logger.info("=" * 50)
        logger.info("🔍 DEBUGGING AUTHENTICATION")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request META AUTH: {request.META.get('HTTP_AUTHORIZATION', 'NOT FOUND')}")
        
        jwt_auth = JWTAuthentication()

        try:
            # Authenticate returns (user, token) or None
            user_auth_tuple = jwt_auth.authenticate(request)
            
            if user_auth_tuple is not None:
                request.user = user_auth_tuple[0]
                logger.info(f"✅ Authenticated user: {request.user.username}")
            else:
                request.user = AnonymousUser()
                logger.info("ℹ️ No authentication credentials provided")
                
        except InvalidToken as e:
            request.user = AnonymousUser()
            logger.warning(f"❌ Invalid token: {str(e)}")
            
        except TokenError as e:
            request.user = AnonymousUser()
            logger.warning(f"❌ Token error: {str(e)}")
            
        except Exception as e:
            request.user = AnonymousUser()
            logger.error(f"❌ Authentication failed: {str(e)}")

        logger.info(f"Final user: {request.user}")
        logger.info(f"Is authenticated: {request.user.is_authenticated}")
        logger.info("=" * 50)
        
        return super().dispatch(request, *args, **kwargs)