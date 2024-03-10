from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from cats.models import Cat, Breed


# List Views
class CatList(LoginRequiredMixin, View):
    def get(self, request):
        breed_count = Breed.objects.count()
        cat_list = Cat.objects.all()

        context = {"breed_count": breed_count, "cat_list": cat_list}
        return render(request, "cats/cat_list.html", context)


class BreedView(LoginRequiredMixin, View):
    def get(self, request):
        breed_list = Breed.objects.all()
        context = {"breed_list": breed_list}
        return render(request, "cats/breed-list.html", context)


# Cats CRUD
class CatCreate(LoginRequiredMixin, CreateView):
    model = Cat
    fields = "__all__"
    success_url = reverse_lazy("cats:all")


class CatUpdate(LoginRequiredMixin, UpdateView):
    model = Cat
    fields = "__all__"
    success_url = reverse_lazy("cats:all")


class CatDelete(LoginRequiredMixin, DeleteView):
    model = Cat
    fields = "__all__"
    success_url = reverse_lazy("cats:all")


# Breed CRUD
class BreedCreate(LoginRequiredMixin, CreateView):
    model = Breed
    fields = "__all__"
    success_url = reverse_lazy("cats:all")


class BreedUpdate(LoginRequiredMixin, UpdateView):
    model = Breed
    fields = "__all__"
    success_url = reverse_lazy("cats:all")


class BreedDelete(LoginRequiredMixin, DeleteView):
    model = Breed
    fields = "__all__"
    success_url = reverse_lazy("cats:all")