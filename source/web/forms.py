from django import forms
from . import models


class ProgramForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(), help_text="Сообщение будет отправлено всем пользователям")
    forms.CharField()

    class Meta:
        model = models.Programs
        fields = {
            'text'
        }
