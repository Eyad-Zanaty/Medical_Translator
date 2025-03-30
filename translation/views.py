from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .serializers import UserSerializer, UserLoginSerializer, TranslationSerializer
from .models import Translation
from .medical_utils import MedicalTerminologyValidator
from .language_detection import detect_language
import requests

# MyMemory Translation API endpoint
MYMEMORY_URL = "https://api.mymemory.translated.net/get"

class RegisterView(APIView):
    """
    API endpoint for user registration
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    """
    API endpoint for user login
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            serializer = UserLoginSerializer(data=request.data)
            if serializer.is_valid():
                username = serializer.validated_data['username']
                password = serializer.validated_data['password']
                user = authenticate(username=username, password=password)
                
                if user:
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({
                        'token': token.key,
                        'user': UserSerializer(user).data
                    })
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    """
    API endpoint for user logout
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out'})
        except ObjectDoesNotExist:
            return Response({'error': 'No active session'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileView(APIView):
    """
    API endpoint for user profile operations
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            serializer = UserSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TranslateView(APIView):
    """
    API endpoint for translation operations
    """
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.medical_validator = MedicalTerminologyValidator()

    def get(self, request):
        """Get all translations for the current user"""
        translations = Translation.objects.filter(user=request.user).order_by('-created_at')
        serializer = TranslationSerializer(translations, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new translation"""
        text = request.data.get('text')
        source_lang = request.data.get('source_lang')
        target_lang = request.data.get('target_lang')

        if not all([text, target_lang]):
            return Response({
                'error': 'Please provide text and target language'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Auto-detect source language if not provided
            if not source_lang or source_lang == 'auto':
                detected_lang, confidence = detect_language(text)
                source_lang = detected_lang

            # Validate medical terms
            validator = MedicalTerminologyValidator()
            suggestions = validator.validate_and_suggest(text)

            # Translate using MyMemory API
            url = f"https://api.mymemory.translated.net/get"
            params = {
                'q': text,
                'langpair': f"{source_lang}|{target_lang}"
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['responseStatus'] == 200:
                translated_text = data['responseData']['translatedText']
                
                # Create translation record
                translation = Translation.objects.create(
                    user=request.user,
                    original_text=text,
                    translated_text=translated_text,
                    source_language=source_lang,
                    target_language=target_lang
                )
                
                return Response({
                    'translated_text': translated_text,
                    'detected_language': source_lang,
                    'medical_suggestions': suggestions if suggestions else []
                })
            else:
                return Response({
                    'error': 'Translation service error'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, translation_id):
        """Delete a translation"""
        try:
            translation = Translation.objects.get(id=translation_id, user=request.user)
            translation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Translation.DoesNotExist:
            return Response({
                'error': 'Translation not found'
            }, status=status.HTTP_404_NOT_FOUND)

class TranslationFavoriteView(APIView):
    """
    API endpoint for toggling translation favorite status
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, translation_id):
        try:
            translation = Translation.objects.get(id=translation_id, user=request.user)
            translation.is_favorite = not translation.is_favorite
            translation.save()
            return Response(TranslationSerializer(translation).data)
        except Translation.DoesNotExist:
            return Response({
                'error': 'Translation not found'
            }, status=status.HTTP_404_NOT_FOUND)