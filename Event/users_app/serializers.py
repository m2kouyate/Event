from collections import OrderedDict
from datetime import date

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        write_only=True,
        min_length=3,
        max_length=50
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
        validators=[RegexValidator(r'^[a-zA-Z]*$', 'Only alphabetic characters are allowed.')],
    )
    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
        validators=[RegexValidator(r'^[a-zA-Z]*$', 'Only alphabetic characters are allowed.')],
    )

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'username',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'date_of_birth',
            'date_registered'
        ]
        read_only_fields = ['id', 'date_registered']

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})

        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})

        return attrs

    def validate_date_of_birth(self, value):
        if value > date.today():
            raise serializers.ValidationError("The date of birth cannot be in the future.")
        return value

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        password_confirm = validated_data.pop('password_confirm', None)
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        profile = UserProfile.objects.create(
            user=user,
            **validated_data
        )

        return profile

    def update(self, instance, validated_data):
        # Обновляем поля модели User
        username = validated_data.pop('username', instance.user.username)
        first_name = validated_data.pop('first_name', instance.user.first_name)
        last_name = validated_data.pop('last_name', instance.user.last_name)
        password = validated_data.pop('password', None)
        password_confirm = validated_data.pop('password_confirm', None)

        instance.user.username = username
        instance.user.first_name = first_name
        instance.user.last_name = last_name

        if password and password == password_confirm:
            instance.user.set_password(password)

        # Обновляем поля модели UserProfile
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.user.save()
        instance.save()

        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if hasattr(instance, 'user'):
            user_instance = instance.user
        else:
            user_instance = instance
        rep['username'] = user_instance.username
        rep['first_name'] = user_instance.first_name
        rep['last_name'] = user_instance.last_name

        ordered_rep = OrderedDict()
        field_order = ['id', 'username', 'first_name', 'last_name', 'date_of_birth', 'date_registered']

        for field in field_order:
            ordered_rep[field] = rep.get(field, None)

        return ordered_rep





