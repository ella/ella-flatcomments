from django.forms.models import ModelForm

from app_data.forms import multiform_factory

from ella_flatcomments.models import FlatComment

class FlatCommentForm(ModelForm):
    def __init__(self, content_object, user, *args, **kwargs):
        self.content_type = content_object
        self.user = user
        super(FlatCommentForm, self).__init__(*args, **kwargs)

        # store the auto fields on the comment instance directly
        self.instance.user = self.user
        self.instance.content_object = self.content_object

    class Meta:
        model = FlatComment
        fields = (
            'content',
        )

FlatCommentMultiForm = multiform_factory(FlatCommentForm)
