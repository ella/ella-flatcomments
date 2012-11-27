# for backwards compatibility, just reuse signals from django.contrib.comments
from django.contrib.comments.signals import comment_will_be_posted, comment_was_posted

from django.dispatch import Signal

comment_was_moderated = Signal(providing_args=['comment', 'user'])

comment_updated = Signal(providing_args=['comment', 'updating_user', 'date_updated'])
