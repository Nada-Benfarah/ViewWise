
from django.conf import settings
import jwt
from accounts.renderers import UserRenderer
from accounts.utils.document_loader import DocumentLoader, Util
from .serializers import LogoutSerializer, RegisterSerializer, EmailVerificationSerializer, LoginSerializer, ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User
from rest_framework.response import Response
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework import generics, status, views, permissions
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.http import HttpResponsePermanentRedirect
from rest_framework.views import APIView
from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework_simplejwt.exceptions import TokenError









class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Send verification email
        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify')
        absurl = 'http://' + current_site + relativeLink + "?token=" + str(access_token)
        email_body = f'Hi {user.username}, use the link below to verify your email:\n{absurl}'
        email_data = {'email_body': email_body, 'to_email': user.email, 'email_subject': 'Verify your email'}
        Util.send_email(email_data)

        # Set cookies
        response = Response(user_data, status=status.HTTP_201_CREATED)
        response.set_cookie(
            key='access_token',
            value=str(access_token),
            httponly=True,
            secure=True,  # Set to True if using HTTPS
            samesite='Lax'
        )
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite='Lax'
        )
        
        return response


class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Email verification token', type=openapi.TYPE_STRING
    )

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        operation_description="Login with email & password. Returns tokens in response and stores them in cookies.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "email": "test@example.com",
                        "username": "testuser",
                        "tokens": {
                            "refresh": "some_refresh_token",
                            "access": "some_access_token"
                        }
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(email=serializer.validated_data['email'], password=request.data['password'])
        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = user.tokens()  # Assurez-vous que `tokens()` retourne {'refresh': ..., 'access': ...}

        response = Response({
            "email": user.email,
            "username": user.username,
            "tokens": tokens
        }, status=status.HTTP_200_OK)

        # Stocker les tokens dans les cookies HTTPOnly
        response.set_cookie(key='access_token', value=tokens['access'], httponly=True, secure=True, samesite='Lax')
        response.set_cookie(key='refresh_token', value=tokens['refresh'], httponly=True, secure=True, samesite='Lax')

        return response


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Déconnexion de l'utilisateur en blacklistant le refresh token et en supprimant les cookies",
        request_body=LogoutSerializer,
        responses={
            200: openapi.Response(
                description="Déconnexion réussie",
                examples={
                    "application/json": {"message": "User logged out successfully"}
                }
            ),
            400: openapi.Response(
                description="Erreur de token",
                examples={
                    "application/json": {"error": "Invalid or expired token"}
                }
            ),
        },
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                description="Token d'authentification (Bearer Token)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data.get('refresh')
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Supprimer les cookies après logout
        response = Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response

   
class RetrieveUserAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Récupérer les informations de l'utilisateur authentifié",
        responses={
            200: UserSerializer(),
            401: openapi.Response(
                description="User unauthenticated",
                examples={
                    "application/json": {
                        "message": "User unauthenticated"
                    }
                }
            )
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization', 
                openapi.IN_HEADER, 
                description="Token d'authentification au format 'Bearer <token>'", 
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    def get(self, request):
        user = request.user
        
        # Vérifier si l'utilisateur est bien authentifié
        if not user.is_authenticated:
            return Response({"message": "User unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            redirect_url = request.data.get('redirect_url', '')
            absurl = 'http://'+current_site + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + \
                absurl+"?redirect_url="+redirect_url
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            Util.send_email(data)
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)



class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'success': True, 'message': 'Credentials Valid', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)

            
        except DjangoUnicodeDecodeError as identifier:
            if not PasswordResetTokenGenerator().check_token(user):
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)

            

class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)






class TestLoaderAPIView(APIView):
    """
    API pour récupérer toutes les URLs du sitemap HTML d'un site.
    """

    @swagger_auto_schema(
        operation_description="Récupère toutes les URLs du sitemap HTML d'un site.",
        responses={200: openapi.Response("Liste des URLs trouvées", openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'urls': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING)
                )
            }
        ))}
    )
    def get(self, request):
        """Charge et retourne les URLs du sitemap HTML."""
        loader = DocumentLoader()
        test_url = "https://inveep.com/en/"
        urls = loader.get_urls_from_html_sitemap(test_url)
        return Response({"urls": urls})