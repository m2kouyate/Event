from datetime import date

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import UserProfile


class ProfileRegistrationForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'max': date.today().strftime('%Y-%m-%d')
            }
        )
    )

    class Meta:
        model = UserProfile
        fields = ['date_of_birth']

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth and date_of_birth > date.today():
            raise forms.ValidationError("The date of birth cannot be in the future.")
        return date_of_birth


class ProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = UserProfile
        fields = ['date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date',
                    'max': date.today().strftime('%Y-%m-%d')
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            user = self.instance.user
            self.fields['username'].initial = user.username
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['date_of_birth'].initial = self.instance.date_of_birth

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth and date_of_birth > date.today():
            raise forms.ValidationError("The date of birth cannot be in the future.")
        return date_of_birth


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Например: : SecureP@ss123'}))
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}))
    username = forms.CharField(
        max_length=150,
        help_text='',
        widget=forms.TextInput(attrs={'placeholder': 'Например: : johndoe123'})
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Например: : John'})
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Например: : Doe'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают.')
        validate_password(cd['password'])
        return cd['password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует.')
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name.isalpha():
            raise forms.ValidationError("Имя может содержать только буквы")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name.isalpha():
            raise forms.ValidationError("Фамилия может содержать только буквы")
        return last_name



