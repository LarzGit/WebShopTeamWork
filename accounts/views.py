from django.contrib.auth import authenticate, login, logout
from orders.models import Order
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, ProfileSerializer, OrderHistorySerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                return Response({"detail": "Акаунт заблоковано"}, status=status.HTTP_403_FORBIDDEN)
            login(request, user)
            return Response({"detail": "login success user ", "username": user.username})
        return Response({"detail": "login password error"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"detail": "enter success"}, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        ordering = self.request.query_params.get('ordering', '-created_at')
        allowed = {'created_at', '-created_at', 'status', '-status'}
        if ordering not in allowed:
            ordering = '-created_at'
        return queryset.order_by(ordering)