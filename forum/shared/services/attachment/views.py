from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers

from .serializers import AttachmentSerializer

class AttachmentUploadAPIView(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, *args, **kwargs):
        serializer = AttachmentSerializer(data=request.data)
        if serializer.is_valid():
            attachment = serializer.save()
            return Response({'id': attachment.id, 'file': attachment.file.url}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
