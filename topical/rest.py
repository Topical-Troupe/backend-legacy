from rest_framework import routers, viewsets

from .models import User
from .serializers import UserSerializer

router = routers.DefaultRouter()

class UserSerializer(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	lookup_field = 'username'
