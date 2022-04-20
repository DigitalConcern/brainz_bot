from django.views.generic import TemplateView, CreateView, UpdateView
from django.urls import reverse_lazy
import asyncio
from . import models
from . import forms


class HomePageView(TemplateView):
    template_name = 'home.html'


class UsersPageView(TemplateView):
    model = models.ActiveUsers
    template_name = 'users.html'
    # fields = ['user_id', 'code_name']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = models.ActiveUsers.objects.all()
        return context


class MailingPageView(CreateView):
    template_name = 'mailing.html'
    form_class = forms.CommentForm
    success_url = reverse_lazy('home')
