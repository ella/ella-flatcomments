from django import forms
from django.forms.models import ModelForm

from app_data.forms import MultiForm

from ella_flatcomments.models import FlatComment

class FlatCommentForm(ModelForm):
    # copied over from django.contrib.comments.forms.CommentForm
    honeypot = forms.CharField(
        required=False,
        label='If you enter anything in this field your comment will be treated as spam'
    )

    def __init__(self, content_object, user, *args, **kwargs):
        self.content_object = content_object
        self.user = user
        super(FlatCommentForm, self).__init__(*args, **kwargs)

        # store the auto fields on the comment instance directly
        self.instance.user = self.user
        self.instance.content_object = self.content_object

    def clean_honeypot(self):
        """Check that nothing's been entered into the honeypot."""
        value = self.cleaned_data["honeypot"]
        if value:
            raise forms.ValidationError(self.fields["honeypot"].label)
        return value


    class Meta:
        model = FlatComment
        fields = (
            'comment',
        )

class FlatCommentMultiForm(MultiForm):
    ModelForm = FlatCommentForm

    def post(self):
        comment = super(FlatCommentMultiForm, self).save(commit=False)
        success, reason = comment.post()
        return comment, success, reason
