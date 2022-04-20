from django import forms
from . import models


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(), help_text="Сообщение будет отправлено всем пользователям")

    class Meta:
        model = models.Programs
        fields = {
            'text'
        }
