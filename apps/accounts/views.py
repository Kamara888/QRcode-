from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = User.objects.all()
        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(role=role)
        return qs


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
