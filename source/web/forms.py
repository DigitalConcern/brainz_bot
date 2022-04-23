from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import Accordion, AccordionGroup
from django import forms
from django.forms import TextInput, Textarea, ChoiceField,Select,CheckboxInput
from django.shortcuts import render

from . import models
from crispy_forms.layout import Field, Layout


# class ProgramForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.layout = Layout(
#             Accordion(
#                 AccordionGroup('First Group',
#                                'radio_buttons'
#                                ),
#                 AccordionGroup('First Group',
#                                'radio_buttons'
#                                ),
#             )
#         )

class ProgramForm(forms.ModelForm):
    class Meta:
        model = models.Programs
        fields = ['name', 'description', 'info', 'category', 'is_active', 'link']
        widgets = {
            "name": TextInput(attrs={'class': 'form-control', 'placeholder': 'Название'}),
            "description": Textarea(attrs={'class': 'form-control', 'style': 'height: 100px', 'placeholder': 'Краткое '
                                                                                                             'описание'}),
            "info": Textarea(attrs={'class': 'form-control', 'style': 'height: 200px', 'placeholder': 'q'}),
            "category": Select(attrs={'class': 'form-select'}  , choices=(('students', 'Студенты'), ('school', 'Школьники'))),
            "is_active": CheckboxInput(attrs={'class': 'form-check-input','role': 'switch'}),
            "link": TextInput(attrs={'class': 'form-control', 'placeholder': 'r'}),

        }
