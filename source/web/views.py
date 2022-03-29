from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
import asyncio
from bot.main import bot
from . import models
from . import forms


class HomePageView(TemplateView):
    template_name = 'home.html'


class UsersPageView(TemplateView):
    template_name = 'users.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = models.User.objects.all()
        return context


class MailingPageView(CreateView):
    template_name = 'mailing.html'
    form_class = forms.CommentForm
    success_url = reverse_lazy('home')

    def get_success_url(self) -> str:
        text = self.request.POST.get('text')
        # bot = Bot("BOT_API_TOKEN")
        for user in models.User.objects.all():
            bot.send_message(user.tg_id, text, parse_mode="HTML")
        return super().get_success_url()
