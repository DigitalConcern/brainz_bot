from django.contrib import messages
from django.forms import TextInput
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
import asyncio
from . import models
from . import forms
from .forms import ProgramForm
from django.utils.translation import gettext as _


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


# class ProgramsPageView(TemplateView):
#     model = models.Programs
#     template_name = 'programs.html'
#     # form_class = forms.CommentForm
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['programs'] = models.Programs.objects.all()
#         return context


class ProgramsPageView(TemplateView):
    model = models.Programs
    template_name = "programs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['programs'] = models.Programs.objects.all()
        return context


class CreateProgView(CreateView):
    model = models.Programs
    template_name = "programs/create.html"
    fields = ['id', 'key', 'name', 'description']

    # data = {'form': ProgramForm()}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProgramForm
        return context

    def get_success_url(self) -> str:
        print("done")
        return render(self, 'programs/create.html')
    # def create(self):
    #     form = ProgramForm()
    #     data = {'form': form}
    #     return render(self, 'programs/create.html')


class ProgramsEditView(UpdateView):
    model = models.Programs
    template_name = "programs/create.html"
    form_class = ProgramForm

    # def get(self, request, *args, **kwargs):
    #     return super().get(request, *args, **kwargs)
    #
    # def post(self, request, *args, **kwargs):
    #     return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # pw = form.cleaned_data["password1"]
        # if pw != "":
        #     self.object.set_password(pw)
        self.object.save()
        messages.info(self.request, _("Account info saved!"))
        return redirect("/programs")

        # fields = ['id', 'key', 'name', 'description']
    # widgets = {
    #     "id": TextInput(attrs={'class': 'form-control', 'placeholder': 'ID'}),
    #     "key": TextInput(attrs={'class': 'form-control', 'placeholder': 'key'}),
    #     "name": TextInput(attrs={'class': 'form-control', 'placeholder': 'Название'}),
    #     "description": TextInput(attrs={'class': 'form-control', 'placeholder': 'Краткое описание'})
    # }


class ProgramsDeleteView(DeleteView):
    model = models.Programs
    template_name = "programs/delete.html"
    success_url = "/programs"
