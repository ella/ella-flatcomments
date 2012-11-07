import sys

from django.core.management.base import NoArgsCommand
from django.contrib import comments

from ella_flatcomments.models import FlatComment, CommentList

class Command(NoArgsCommand):
    def handle_noargs(self, **kwargs):

        CommentModel = comments.get_model()

        for c in CommentModel.objects.exclude(user__isnull=True).sort('submit_date').iterator():
            fc = FlatComment(
                site_id=c.site_id,
                content_type_id=c.content_type_id,
                object_id=c.object_pk,
                user_id=c.user_id,
                submit_date=c.submit_date,
                content=c.comment,
                is_public=c.is_public and not c.is_removed
            )

            if fc.is_public:
                cl = CommentList(fc.content_type, fc.object_id)
                cl.post_comment(fc)
                sys.stdout.write('.'); sys.stdout.flush()
            else:
                fc.save(force_insert=True)
                sys.stdout.write('X'); sys.stdout.flush()
        sys.stdout.write('DONE\n'); sys.stdout.flush()
