from rest_framework.views import APIView

from .models import Comment
from .serializers import CommentSerializer


class CommentsAPIView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        pass