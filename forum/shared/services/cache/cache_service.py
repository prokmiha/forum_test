from django.core.cache import cache
from django.utils.timezone import now
from django.conf import settings

from core.domains.comments.models import Comment
from core.domains.comments.serializers import CommentSerializer

TOP_KEY = "comment:top"
REPLIES_KEY = "replies:{parent_id}:offset:{offset}:limit:{limit}"
NESTED_REPLIES_KEY = "nested_replies:{parent_id}"
MAX_TOP_COMMENTS = 5000
FIXED_TOP_HEAD = 100
MAX_REPLY_KEYS = 2000

class CommentCacheService:

    @staticmethod
    def get_top_comments():
        data = cache.get("comment:top")
        if not data:
            return None
        return [dict(item) for item in data]

    @staticmethod
    def add_top_comment(comment_data):
        top = cache.get(TOP_KEY, [])
        comment_data['cached_at'] = now().isoformat()

        fixed_head = top[:FIXED_TOP_HEAD]
        tail = top[FIXED_TOP_HEAD:]

        tail.insert(0, comment_data)
        allowed_tail = tail[:MAX_TOP_COMMENTS - len(fixed_head)]

        new_cache = fixed_head + allowed_tail
        cache.set(TOP_KEY, new_cache)

    @staticmethod
    def set_top_comments(comment_list):
        cache.set("comment:top", comment_list)

    @staticmethod
    def get_replies(parent_id, offset, limit):
        key = REPLIES_KEY.format(parent_id=parent_id, offset=offset, limit=limit)
        return cache.get(key)

    @staticmethod
    def set_replies(parent_id, offset, limit, data):
        key = REPLIES_KEY.format(parent_id=parent_id, offset=offset, limit=limit)
        cache.set(key, data, timeout=settings.COMMENT_CACHE_TTL)

        if hasattr(cache, "sadd"):
            cache.sadd("reply_keys", key)

    @staticmethod
    def build_and_store_top_comments():
        top_level_comments = Comment.objects.filter(parent__isnull=True).order_by('-created_at')[:MAX_TOP_COMMENTS]
        serializer = CommentSerializer(top_level_comments, many=True)
        now_ts = now().isoformat()
        data = serializer.data
        for c in data:
            c["cached_at"] = now_ts
            c["replies"] = []
        cache.set(TOP_KEY, data)

    @staticmethod
    def invalidate_replies(parent_id):
        keys_to_try = {
            REPLIES_KEY.format(parent_id=parent_id, offset=0, limit=50),
            REPLIES_KEY.format(parent_id=parent_id, offset=0, limit=3),
        }
        for key in keys_to_try:
            cache.delete(key)

    @staticmethod
    def set_nested_replies(parent_id, data):
        key = NESTED_REPLIES_KEY.format(parent_id=parent_id)
        cache.set(key, data, timeout=settings.COMMENT_CACHE_TTL)

    @staticmethod
    def invalidate_nested_replies(parent_id):
        cache.delete(NESTED_REPLIES_KEY.format(parent_id=parent_id))
