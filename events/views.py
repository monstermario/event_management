from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.utils.timezone import now
from .models import Event
from .serializers import RegisterSerializer, LoginSerializer, EventSerializer, CustomTokenObtainPariSerializer
from .permissions import IsOwnerOrReadOnly

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPariSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        if self.action == 'list':
            return Event.objects.filter(start_date__gte=now())
        return super().get_queryset()

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAuthenticated])
    def register(self, request, pk=None):
        event = self.get_object()

        if event.start_date < now():
            return Response({'error': 'Cannot register from past events'}, status=status.HTTP_400_BAD_REQUEST)
        
        if event.capacity and event.attendees.count() >= event.capacity:
            return Response({'error': 'Event capacity reached'}, status=status.HTTP_400_BAD_REQUEST)

        event.attendees.add(request.user)
        return Response({'status': 'Registered'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAuthenticated])
    def unregister(self, request, pk=None):
        event = self.get_object()

        if event.start_date < now():
            return Response({'error': 'Cannot unregister from past events'}, status=status.HTTP_400_BAD_REQUEST)

        event.attendees.remove(request.user)
        return Response({'status': 'Unregistered'}, status=status.HTTP_200_OK)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            "message": "Login successful.",
        }, status=status.HTTP_200_OK)
