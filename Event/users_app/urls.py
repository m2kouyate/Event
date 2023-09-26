from django.urls import path
from .views import CustomLoginView, CustomLogoutView, register, profile_detail, ProfileUpdate, ProfileDelete

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('profile/<int:pk>/', profile_detail, name='profile_detail'),
    path('profile/<int:pk>/edit/', ProfileUpdate.as_view(), name='profile_edit'),
    path('profile/<int:pk>/delete/', ProfileDelete.as_view(), name='profile_delete'),
]


