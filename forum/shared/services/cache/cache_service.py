from django.core.cache import cache
from django.utils.timezone import now
from django.conf import settings

from core.domains.comments.models import Comment
from core.domains.comments.serializers import CommentSerializer, ReplySerializer

import logging

TOP_KEY = "comment:top"
REPLIES_KEY = "replies:{parent_id}"
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
    def set_top_comments(comment_list, top_level_comments):
        cache.set("comment:top", comment_list)

        top_comment_ids = [c.id for c in top_level_comments[:FIXED_TOP_HEAD]]

        for parent_id in top_comment_ids:
            replies_qs = Comment.objects.filter(parent_id=parent_id).order_by('-created_at')
            total = replies_qs.count()
            replies = replies_qs[:60]
            serializer = ReplySerializer(replies, many=True)

            data = {
                "results": serializer.data,
                "has_more": total > 60,
                "total": total,
                "offset": 0,
                "limit": 60,
            }

            cache.set(REPLIES_KEY.format(parent_id=parent_id), data, timeout=settings.COMMENT_CACHE_TTL)
        logging.error(cache.keys("*"))


    @staticmethod
    def get_replies(parent_id):
        key = REPLIES_KEY.format(parent_id=parent_id)
        return cache.get(key)

    @staticmethod
    def set_replies(parent_id, data):
        key = REPLIES_KEY.format(parent_id=parent_id)
        cache.set(key, data, timeout=settings.COMMENT_CACHE_TTL)

        if hasattr(cache, "sadd"):
            cache.sadd("reply_keys", key)

    @staticmethod
    def build_and_store_top_comments():
        now_ts = now().isoformat()
        top_level_comments = Comment.objects.filter(parent__isnull=True).order_by('-created_at')[:MAX_TOP_COMMENTS]
        logging.error(len(top_level_comments))
        serializer = CommentSerializer(top_level_comments, many=True)
        top_data = serializer.data
        logging.error(top_data)

        # Добавляем время и структуру
        for item in top_data:
            item["cached_at"] = now_ts
            item["replies"] = item.get("replies", [])
            item["has_more_replies"] = item.get("has_more_replies", False)

        cache.set(TOP_KEY, top_data)
        logging.error(cache.keys("*"))

        # Теперь: создаём replies:{parent_id} для FIXED_TOP_HEAD
        for comment in top_level_comments[:FIXED_TOP_HEAD]:
            logging.error(comment)

            child_qs = Comment.objects.filter(parent=comment).order_by('-created_at')[:60]
            total = Comment.objects.filter(parent=comment).count()
            serializer = ReplySerializer(child_qs, many=True)

            data = {
                "results": serializer.data,
                "has_more": total > 60,
                "total": total,
                "offset": 0,
                "limit": 60,
            }

            key = REPLIES_KEY.format(parent_id=comment.id)
            cache.set(key, data, timeout=settings.COMMENT_CACHE_TTL)
        logging.error(cache.keys("*"))

    @staticmethod
    def invalidate_replies(parent_id):
        key = REPLIES_KEY.format(parent_id=parent_id)

        cache.delete(key)

    @staticmethod
    def set_nested_replies(parent_id, data):
        key = NESTED_REPLIES_KEY.format(parent_id=parent_id)
        cache.set(key, data, timeout=settings.COMMENT_CACHE_TTL)

    @staticmethod
    def invalidate_nested_replies(parent_id):
        cache.delete(NESTED_REPLIES_KEY.format(parent_id=parent_id))

    @staticmethod
    def handle_new_comment(comment):
        """
        Обновляет кэш top или replies, если добавлен новый реплай.
        Если родителя нет в кэше — пересоздает ветку replies:{parent_id}.
        """
        parent_id = comment.parent_id
        if not parent_id:
            return  # это заглавный комментарий

        # 1. Проверка в TOP
        top = cache.get(TOP_KEY) or []
        for item in top:
            if item["id"] == parent_id:
                CommentCacheService._update_top_comment_reply(item, comment)
                cache.set(TOP_KEY, top)
                return

        # 2. Проверка в replies:{}
        key = REPLIES_KEY.format(parent_id=parent_id)
        cached = cache.get(key)
        if cached:
            CommentCacheService._update_replies_entry(cached, comment)
            cache.set(key, cached, timeout=settings.COMMENT_CACHE_TTL)
            return

        # 3. Родителя нет нигде — пересоздаем replies:{parent_id}
        replies = Comment.objects.filter(parent_id=parent_id).order_by('-created_at')
        serializer = ReplySerializer(replies[:3], many=True)
        data = {
            "results": serializer.data,
            "has_more": replies.count() > 3,
            "total": replies.count(),
            "offset": 0,
            "limit": 3,
        }
        cache.set(key, data, timeout=settings.COMMENT_CACHE_TTL)

    @staticmethod
    def _update_top_comment_reply(top_entry, reply):
        top_entry["reply_count"] = top_entry.get("reply_count", 0) + 1
        top_entry["has_more_replies"] = top_entry["reply_count"] > 3
        replies = top_entry.get("replies", [])
        if len(replies) < 3:
            serializer = ReplySerializer(reply)
            replies.insert(0, serializer.data)
        top_entry["replies"] = replies[:3]

    @staticmethod
    def _update_replies_entry(cache_block, reply):
        cache_block["total"] = cache_block.get("total", 0) + 1
        cache_block["has_more"] = cache_block["total"] > 3
        results = cache_block.get("results", [])
        if len(results) < 3:
            serializer = ReplySerializer(reply)
            results.insert(0, serializer.data)
        cache_block["results"] = results[:3]

# from django.core.cache import cache
# from core.domains.comments.models import Comment
# from core.domains.comments.serializers import CommentSerializer
#
# TOP_KEY = "comment:top"
# REPLIES_KEY = "replies:{parent_id}:offset:{offset}:limit:{limit}"
# NESTED_REPLIES_KEY = "nested_replies:{parent_id}"
# MAX_TOP_COMMENTS = 5000
# FIXED_TOP_HEAD = 100
# MAX_REPLY_KEYS = 2000
# COMMENT_CACHE_TTL = 1800
#
# class CommentCacheService:
#
#     @staticmethod
#     def get_top_comments():
#         return cache.get(TOP_KEY, [])
#
#     @staticmethod
#     def set_top_comments(comments):
#         cache.set(TOP_KEY, comments, timeout=None)
#
#     @staticmethod
#     def add_top_comment(comment_data):
#         top = CommentCacheService.get_top_comments()
#         top.insert(0, comment_data)
#         fixed = top[:FIXED_TOP_HEAD]
#         dynamic = top[FIXED_TOP_HEAD:5000]
#         CommentCacheService.set_top_comments(fixed + dynamic)
#
#     @staticmethod
#     def get_replies(parent_id, offset, limit):
#         key = REPLIES_KEY.format(parent_id=parent_id, offset=offset, limit=limit)
#         return cache.get(key)
#
#     @staticmethod
#     def set_replies(parent_id, offset, limit, data):
#         key = REPLIES_KEY.format(parent_id=parent_id, offset=offset, limit=limit)
#         cache.set(key, data, timeout=COMMENT_CACHE_TTL)
#
#         if hasattr(cache, "sadd"):
#             cache.sadd("reply_keys", key)
#
#     @staticmethod
#     def update_top_comment_replies(comment_id):
#         top = CommentCacheService.get_top_comments()
#         for item in top:
#             if item['id'] == comment_id:
#                 try:
#                     comment = Comment.objects.get(id=comment_id)
#                 except Comment.DoesNotExist:
#                     continue
#                 serializer = CommentSerializer(comment)
#                 item.update({
#                     "reply_count": serializer.data.get("reply_count"),
#                     "has_more_replies": serializer.data.get("has_more_replies"),
#                     "replies": serializer.data.get("replies")
#                 })
#                 break
#         CommentCacheService.set_top_comments(top)
#
#     @staticmethod
#     def invalidate_replies(comment_id):
#         key = CommentCacheService.get_replies_key(comment_id, 0, 3)
#         data = cache.get(key)
#         if data:
#             cache.set(key, data, timeout=COMMENT_CACHE_TTL)
#
#     @staticmethod
#     def set_nested_replies(parent_id, data):
#         key = NESTED_REPLIES_KEY.format(parent_id=parent_id)
#         cache.set(key, data, timeout=COMMENT_CACHE_TTL)
#
#     @staticmethod
#     def invalidate_nested_replies(parent_id):
#         cache.delete(NESTED_REPLIES_KEY.format(parent_id=parent_id))
#
#     @staticmethod
#     def update_replies_cache(comment_id, new_reply=None):
#         key = CommentCacheService.get_replies_key(comment_id, 0, 3)
#         data = cache.get(key)
#         replies = data or []
#         if new_reply:
#             replies.insert(0, new_reply)
#         cache.set(key, replies[:3], timeout=COMMENT_CACHE_TTL)
#
#     @staticmethod
#     def get_replies_key(parent_id, offset, limit):
#         return f"replies:{parent_id}:offset:{offset}:limit:{limit}"
