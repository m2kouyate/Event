from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from rest_framework import viewsets, status
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .forms import ProfileRegistrationForm, ProfileUpdateForm, UserRegistrationForm
from .models import UserProfile
from .serializers import UserProfileSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all().select_related('user').order_by('-date_registered')
    serializer_class = UserProfileSerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            raise PermissionDenied("Authenticated users cannot create new profiles.")
        serializer.save()

    def check_owner(self, instance):
        if self.request.user != instance.user:
            raise PermissionDenied("You don't have permission to modify this profile.")

    def perform_update(self, serializer):
        self.check_owner(self.get_object())
        serializer.save()

    def perform_destroy(self, instance):
        self.check_owner(instance)
        instance.delete()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"error": None, "result": serializer.data}, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"error": None, "result": serializer.data}, status=status.HTTP_200_OK)


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, "Ошибка входа. Пожалуйста, проверьте ваши учетные данные и попробуйте снова.")
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('event_app:events')


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileRegistrationForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            new_profile = profile_form.save(commit=False)
            new_profile.user = new_user
            new_profile.save()
            login(request, authenticate(username=new_user.username, password=user_form.cleaned_data['password']))
            return redirect('users_app:profile_detail', pk=new_profile.pk)
        else:
            messages.error(request, "Ошибка регистрации. Пожалуйста, проверьте введенные данные и попробуйте снова.")
    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileRegistrationForm()
    return render(request, 'users/register.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def profile_detail(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    return render(request, 'users/profile_detail.html', {'profile': profile})


class ProfileUpdate(UpdateView):
    model = UserProfile
    form_class = ProfileUpdateForm
    template_name = 'users/profile_edit.html'

    def get_queryset(self):
        return UserProfile.objects.select_related('user')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            return HttpResponseForbidden("Вы не можете редактировать этот профиль.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        profile = form.save(commit=False)

        user = profile.user
        new_username = form.cleaned_data['username']

        # Проверяем, изменено ли имя пользователя и существует ли уже такое имя
        if user.username != new_username:
            if User.objects.filter(username=new_username).exists():
                form.add_error('username', 'Пользователь с таким именем уже существует.')
                return self.form_invalid(form)

        user.username = new_username
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        profile.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('users_app:profile_detail', kwargs={'pk': self.object.pk})


class ProfileDelete(DeleteView):
    model = UserProfile
    template_name = 'users/profile_confirm_delete.html'
    success_url = reverse_lazy('users_app:register')

    def get_queryset(self):
        return UserProfile.objects.select_related('user')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            return HttpResponseForbidden("Вы не можете удалить этот профиль.")
        return super().dispatch(request, *args, **kwargs)



