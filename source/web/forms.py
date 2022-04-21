from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import Accordion, AccordionGroup
from django import forms
from . import models
from crispy_forms.layout import Field, Layout


class ProgramForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Accordion(
                AccordionGroup('First Group',
                               'radio_buttons'
                               ),
                AccordionGroup('First Group',
                               'radio_buttons'
                               ),
            )
        )
