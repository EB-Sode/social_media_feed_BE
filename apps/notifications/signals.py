# """
# Signals to auto-create notifications when key events happen.
# """

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from apps.posts.models import Post, Like, Comment
# from apps.follows.models import Follow
# from .models import Notification


# @receiver(post_save, sender=Like)
# def notify_like(sender, instance, created, **kwargs):
#     if created:
#         post = instance.post
#         liker = instance.user
#         recipient = post.author
#         if liker != recipient:
#             Notification.objects.create(
#                 recipient=recipient,
#                 sender=liker,
#                 notification_type="like",
#                 post=post,
#                 message="liked your post",
#             )


# @receiver(post_save, sender=Comment)
# def notify_comment(sender, instance, created, **kwargs):
#     if created:
#         post = instance.post
#         commenter = instance.user
#         recipient = post.author
#         if commenter != recipient:
#             Notification.objects.create(
#                 recipient=recipient,
#                 sender=commenter,
#                 notification_type="comment",
#                 post=post,
#                 message="commented on your post",
#             )


# @receiver(post_save, sender=Follow)
# def notify_follow(sender, instance, created, **kwargs):
#     if created:
#         follower = instance.follower
#         followed = instance.followed
#         if follower != followed:
#             Notification.objects.create(
#                 recipient=followed,
#                 sender=follower,
#                 notification_type="follow",
#                 message="started following you",
#             )
