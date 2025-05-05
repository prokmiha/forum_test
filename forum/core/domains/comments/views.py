from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from urllib.parse import urlencode
from django.core.cache import cache

from .models import Comment
from .serializers import CommentSerializer, ReplySerializer
from shared.services.attachment.models import Attachments
from shared.services.validation.sanitizer import sanitize_comment_data
from shared.services.cache.cache_service import CommentCacheService
from shared.services.events.events import captcha_failed, reply_created


class CommentsAPIView(APIView):
    def get(self, request):
        all_comments = CommentCacheService.get_top_comments()

        if not all_comments:
            top_level_comments = Comment.objects.filter(parent__isnull=True).order_by('-created_at')[:1000]
            serializer = CommentSerializer(top_level_comments, many=True)
            now_ts = now().isoformat()
            all_comments = serializer.data
            for c in all_comments:
                c["cached_at"] = now_ts
                c["replies"] = c.get("replies", [])
                c["has_more_replies"] = c.get("has_more_replies", False)

            CommentCacheService.set_top_comments(all_comments, top_level_comments)

        limit = int(request.GET.get("limit", 25))
        offset = int(request.GET.get("offset", 0))
        count = len(all_comments)

        actual_ids = list(
            Comment.objects
            .filter(parent__isnull=True)
            .order_by('-created_at')
            .values_list('id', flat=True)[offset:offset + limit]
        )
        cached_ids = [c["id"] for c in all_comments[offset:offset + limit]]

        if actual_ids != cached_ids:
            CommentCacheService.build_and_store_top_comments()
            all_comments = cache.get("comment:top") or []

        page = all_comments[offset:offset + limit]

        def build_link(new_offset):
            base_url = request.build_absolute_uri(request.path)
            params = request.GET.copy()
            params["offset"] = new_offset
            params["limit"] = limit
            return f"{base_url}?{urlencode(params, doseq=True)}"

        next_link = build_link(offset + limit) if offset + limit < count else None
        prev_link = build_link(max(offset - limit, 0)) if offset > 0 else None

        return Response({
            "count": count,
            "next": next_link,
            "previous": prev_link,
            "results": page
        }, status=status.HTTP_200_OK)

    def post(self, request):
        return processor(request=request)


class CommentRepliesAPIView(APIView):
    def get(self, request, parent_id):
        MAX_LIMIT_CACHE = 50
        offset = int(request.GET.get('offset', 0))
        limit = min(int(request.GET.get('limit', 3)), MAX_LIMIT_CACHE)

        cached = CommentCacheService.get_replies(parent_id)
        if cached:
            return Response({
                "results": cached["results"][offset:offset + limit],
                "total": cached["total"],
                "offset": offset,
                "limit": limit,
                "has_more": offset + limit < cached["total"],
            })

        replies = Comment.objects.filter(parent_id=parent_id).order_by('-created_at')
        total = replies.count()
        subset = replies[offset:offset + limit]
        serializer = ReplySerializer(subset, many=True)

        data = {
            "results": serializer.data,
            "has_more": offset + limit < total,
            "total": total,
            "offset": 0,
            "limit": limit,
        }

        CommentCacheService.set_replies(parent_id, data)
        print(123)
        return Response({
            "results": data["results"][offset:offset + limit],
            "total": total,
            "offset": offset,
            "limit": limit,
            "has_more": offset + limit < total,
        })

    def post(self, request, parent_id):
        return processor(request=request, parent_id=parent_id)


def processor(request, parent_id=None):
    captcha_value = request.data.get("captcha_value")
    captcha_text = request.session.get("captcha_text")
    if not captcha_value or captcha_value.lower() != (captcha_text or "").lower():
        captcha_failed.send(sender=None, ip=request.META.get('REMOTE_ADDR'), value=captcha_value)
        return Response({"error": "Неверная капча"}, status=status.HTTP_400_BAD_REQUEST)

    if "captcha_text" in request.session:
        del request.session["captcha_text"]

    try:
        clean_data = sanitize_comment_data(request.data.copy())
        clean_data['parent'] = parent_id
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    files = request.FILES.getlist("attachments")
    serializer = ReplySerializer(data=clean_data) if parent_id else CommentSerializer(data=clean_data)

    if serializer.is_valid():
        instance = serializer.save()

        CommentCacheService.handle_new_comment(instance)

        if not parent_id:
            data = CommentSerializer(instance).data
            CommentCacheService.add_top_comment(data)

        for file in files:
            Attachments.objects.create(
                comment=instance,
                file=file,
                file_type=file.content_type.split('/')[0] if file.content_type.startswith(('image/', 'text/')) else 'text'
            )

        if parent_id:
            CommentCacheService.invalidate_replies(parent_id)
            CommentCacheService.invalidate_nested_replies(parent_id)

        response_serializer = ReplySerializer(instance) if parent_id else CommentSerializer(instance)
        reply_created.send(sender=instance, ip=request.META.get('REMOTE_ADDR'), data=response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def get_next_prev_links(request, offset, limit, count):
    base = request.build_absolute_uri(request.path)
    params = dict(request.GET)

    def make_link(offset_val):
        params.update({"limit": limit, "offset": offset_val})
        return f"{base}?{urlencode(params, doseq=True)}"

    next_link = make_link(offset + limit) if offset + limit < count else None
    prev_link = make_link(max(offset - limit, 0)) if offset > 0 else None

    return next_link, prev_link
