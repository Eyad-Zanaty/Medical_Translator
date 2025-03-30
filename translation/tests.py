from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Translation
from .medical_utils import MedicalTerminologyValidator
from unittest.mock import patch

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_login(self):
        # Create user first
        User.objects.create_user(**self.user_data)
        
        # Try logging in
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)

class TranslationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        self.translate_url = reverse('translate')

    @patch('translation.views.requests.get')
    def test_translation_creation(self, mock_get):
        # Mock MyMemory API response
        mock_get.return_value.json.return_value = {
            'responseStatus': 200,
            'responseData': {
                'translatedText': 'Hola'
            }
        }
        
        data = {
            'text': 'Hello',
            'source_lang': 'en',
            'target_lang': 'es'
        }
        response = self.client.post(self.translate_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('translated_text' in response.data)
        self.assertTrue(Translation.objects.filter(user=self.user).exists())

    def test_translation_history(self):
        # Create some translations
        Translation.objects.create(
            user=self.user,
            original_text='Hello',
            translated_text='Hola',
            source_language='en',
            target_language='es'
        )
        
        response = self.client.get(self.translate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

class MedicalUtilsTests(TestCase):
    def setUp(self):
        self.validator = MedicalTerminologyValidator()

    @patch('translation.medical_utils.MedicalTerminologyValidator._load_medical_terms')
    def test_medical_term_validation(self, mock_load_terms):
        # Mock medical terms
        mock_load_terms.return_value = ['hypertension', 'diabetes', 'asthma']
        validator = MedicalTerminologyValidator()
        
        text = "The patient has hypertension"
        suggestions = validator.validate_and_suggest(text)
        self.assertEqual(len(suggestions), 0)  # No suggestions since term is correct

    @patch('translation.medical_utils.MedicalTerminologyValidator._load_medical_terms')
    def test_non_medical_term_validation(self, mock_load_terms):
        # Mock medical terms
        mock_load_terms.return_value = ['hypertension', 'diabetes', 'asthma']
        validator = MedicalTerminologyValidator()
        
        text = "Hello world"
        suggestions = validator.validate_and_suggest(text)
        self.assertEqual(len(suggestions), 0)  # No suggestions for non-medical terms
