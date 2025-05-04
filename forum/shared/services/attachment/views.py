from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers

from .serializers import AttachmentSerializer

class AttachmentUploadAPIView(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, *args, **kwargs):
        import logging
        logging.critical(f"post in AttachmentUploadAPIView - request.data: {request.data}")
        serializer = AttachmentSerializer(data=request.data)
        if serializer.is_valid():
            logging.critical(f"post in AttachmentUploadAPIView - serializer.is_valid(): {serializer.is_valid()}")
            attachment = serializer.save()
            return Response({'id': attachment.id, 'file': attachment.file.url}, status=status.HTTP_201_CREATED)
        logging.critical(f"post in AttachmentUploadAPIView - serializer.errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
