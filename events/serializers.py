from django.core.validators import EmailValidator
from django.utils.timezone import now, is_naive, make_aware
from django.utils.dateparse import parse_datetime
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import re
from .models import Event

ERROR_INVALID_CREDENTIALS = 'Invalid credentials or account is inactive'
ERROR_EMAIL_EXISTS = 'User with that email already exists'
ERROR_PASSWORD_MISMATCH = 'Passwords do not match'
ERROR_PASSWORD_REQUIREMENTS = 'Password must contain at least one uppercase letter and one digit.'
ERROR_CAPACITY_REQUIREMENTS = 'Capacity must be a positive integer.'
ERROR_START_DATE_REQUIREMENTS = 'Start date cannot be in the past.'
ERROR_END_DATE_REQUIREMENTS = 'End date cannot be before the start date.'

class CustomTokenObtainPariSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'password']

    def validate(self, attrs):
        user = authenticate(**attrs)
        if not user:
            raise serializers.ValidationError(ERROR_INVALID_CREDENTIALS)
        return user

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[EmailValidator()])
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2', 'first_name', 'last_name']
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(ERROR_EMAIL_EXISTS)
        return value
    
    def validate_password(self, value):
        if not re.match(r'^(?=.*[A-Z])(?=.*\d)', value):
            raise serializers.ValidationError(ERROR_PASSWORD_REQUIREMENTS)
        return value
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': ERROR_PASSWORD_MISMATCH})
        return data
   
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        
        return user

class EventSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    attendees = serializers.SlugRelatedField(
        many=True,
        slug_field='username',
        queryset=User.objects.all(),
        required=False
    )

    class Meta:
        model = Event
        fields = '__all__'

    def validate_start_date(self, value):
        if is_naive(value):
            value = make_aware(value)
        if value < now():
            raise serializers.ValidationError(ERROR_START_DATE_REQUIREMENTS)
        return value

    def validate_end_date(self, value):
        start_date_str = self.initial_data.get('start_date')
        start_date = parse_datetime(start_date_str) if start_date_str else None
        if start_date and is_naive(start_date):
            start_date = make_aware(start_date)
        if is_naive(value):
            value = make_aware(value)
        if start_date and value < start_date:
            raise serializers.ValidationError(ERROR_END_DATE_REQUIREMENTS)
        return value

    def validate(self, data):
        capactity = data.get('capacity')
        if capactity is not None and capactity < 0:
            raise serializers.ValidationError(ERROR_CAPACITY_REQUIREMENTS)

        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(ERROR_END_DATE_REQUIREMENTS)
        return data
