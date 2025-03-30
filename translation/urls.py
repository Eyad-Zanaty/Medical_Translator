from django.urls import path
from .views import (
    TranslateView,
    TranslationFavoriteView,
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView
)

urlpatterns = [
    # Auth endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),

    # Translation endpoints
    path('translate/', TranslateView.as_view(), name='translate'),
    path('translations/', TranslateView.as_view(), name='translation-list'),
    path('translations/<int:translation_id>/', TranslateView.as_view(), name='translation-detail'),
    path('translations/<int:translation_id>/toggle_favorite/', TranslationFavoriteView.as_view(), name='translation-favorite'),
]