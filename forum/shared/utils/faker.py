import random
from faker import Faker
from core.domains.comments.models import Comment

fake = Faker()

def create_comment(parent=None, main_thread=None, depth=0, max_depth=15, max_replies=5):
    if depth > max_depth:
        return

    import logging
    logging.error("create_comment")

    comment = Comment.objects.create(
        user_name=fake.user_name(),
        email=fake.email(),
        text=fake.paragraph(),
        parent=parent,
    )
    logging.error(comment)

    if parent is None:
        comment.main_thread = comment.id
        comment.save()
        main_thread = comment.id
    else:
        main_thread = main_thread

        if isinstance(main_thread, Comment):
            main_thread = main_thread.id
        comment.main_thread = main_thread
        comment.save()
    logging.error(main_thread)

    num_replies = random.randint(0, max_replies)
    logging.error(num_replies)
    for _ in range(num_replies):
        create_comment(
            parent=comment,
            main_thread=main_thread,
            depth=depth + 1,
            max_depth=max_depth,
            max_replies=max_replies
        )
