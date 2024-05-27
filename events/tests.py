from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status, serializers
from django.contrib.auth.models import User
from .models import Event
from .serializers import EventSerializer
from django.utils.timezone import now, timedelta

class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', email='testuser@example.com')

    def test_create_user(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

class RegisterViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'Password123',
            'password2': 'Password123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post('/api/register', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'newuser')

class LoginViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', email='testuser@example.com')

    def test_login_user(self):
        data = {'username': 'testuser', 'password': 'password123'}
        response = self.client.post('/api/login', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class EventViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', email='testuser@example.com')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.event = Event.objects.create(
            name='Test Event',
            start_date=now() + timedelta(days=1),
            end_date=now() + timedelta(days=2),
            created_by=self.user
        )

    def test_list_events(self):
        response = self.client.get('/api/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Event')

    def test_create_event(self):
        data = {
            'name': 'New Event',
            'description': 'This is New Event',
            'start_date': (now() + timedelta(days=3)).isoformat(),
            'end_date': (now() + timedelta(days=4)).isoformat()
        }
        response = self.client.post('/api/events/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(Event.objects.get(id=response.data['id']).name, 'New Event')

    def test_register_for_event(self):
        response = self.client.post(f'/api/events/{self.event.id}/register/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.user, self.event.attendees.all())

    def test_unregister_from_event(self):
        self.event.attendees.add(self.user)
        response = self.client.post(f'/api/events/{self.event.id}/unregister/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.user, self.event.attendees.all())

    def test_create_past_event(self):
        data = {
            'name': 'Past Event',
            'start_date': (now() - timedelta(days=3)).isoformat(),
            'end_date': (now() - timedelta(days=2)).isoformat()
        }
        response = self.client.post('/api/events/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_capacity(self):
        self.event.capacity = 1
        self.event.save()
        self.event.attendees.add(self.user)
        response = self.client.post(f'/api/events/{self.event.id}/register/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class EventSerializerTestCase(TestCase):
    def test_validate_start_date(self):
        serializer = EventSerializer(data={'start_date': now() - timedelta(days=1)})
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_validate_end_date(self):
        data = {
            'start_date': (now() + timedelta(days=1)).isoformat(),
            'end_date': (now() - timedelta(days=1)).isoformat()
        }
        serializer = EventSerializer(data=data)
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_validate_capacity(self):
        serializer = EventSerializer(data={'capacity': -1})
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)