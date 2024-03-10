from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Ad, Comment, Fav
from .owner import (
    OwnerDetailView,
    OwnerDeleteView,
)
from .forms import CommentForm, CreateForm


############
# Ad Views #
############
class AdListView(View):
    """Shows all ads in a list"""

    template_name = "ads/ad_list.html"

    def get(self, request):
        search_str = request.GET.get("search", False)
        # If there is a search
        if search_str:
            query = Q(title__icontains=search_str)
            query.add(Q(text__icontains=search_str), Q.OR)
            query.add(Q(tags__name__in=[search_str]), Q.OR)
            # select_related preloads the one to many relationship to avoid consulting the database twice (https://docs.djangoproject.com/en/4.2/ref/models/querysets/#django.db.models.query.QuerySet.select_related)
            ad_list = Ad.objects.filter(query).select_related().distinct()
        else:
            ad_list = Ad.objects.all()

        # Determine favorites
        favorites = list()
        if request.user.is_authenticated:
            rows = request.user.favorite_ads.values("id")
            favorites = [row["id"] for row in rows]

        ctx = {"ad_list": ad_list, "favorites": favorites, "search": search_str}
        return render(request, self.template_name, ctx)


class AdDetailView(OwnerDetailView):
    model = Ad
    template_name = "ads/ad_detail.html"

    def get(self, request, pk: int):
        """Gets and displays the ad with its comments and a form to add more comments

        Args:
            request (HttpRequest): The current request
            pk (int): The primary key of the ad

        Returns:
            HttpResponse: The page with the ad, comments and comment form
        """
        ad = get_object_or_404(Ad, id=pk)
        comments = Comment.objects.filter(ad=ad).order_by("-updated_at")
        comment_form = CommentForm()
        context = {"ad": ad, "comments": comments, "comment_form": comment_form}
        return render(request, self.template_name, context)


class AdCreateView(LoginRequiredMixin, View):
    template_name = "ads/ad_form.html"
    success_url = reverse_lazy("ads:all")

    def get(self, request):
        """Gets and displays a form to create an ad

        Args:
            request (HttpRequest): The current request

        Returns:
            HttpResponse: The response filled with the form
        """
        form = CreateForm()
        context = {"form": form}
        return render(request, template_name=self.template_name, context=context)

    def post(self, request):
        """Posts the new ad information

        Args:
            request (HttpRequest): The current request

        Returns:
            HttpResponse | HttpResponseRedirect: The response filled with the form if there was an error, or a redirected response if it was successful
        """
        form = CreateForm(request.POST, request.FILES or None)

        # If there are errors
        if not form.is_valid():
            context = {"form": form}
            return render(request, template_name=self.template_name, context=context)

        # Add an owner
        ad = form.save(commit=False)
        ad.owner = self.request.user
        ad.save()
        form.save_m2m()  # To save tags
        return redirect(self.success_url)


class AdUpdateView(LoginRequiredMixin, View):
    template_name = "ads/ad_form.html"
    success_url = reverse_lazy("ads:all")

    def get(self, request, pk: int):
        """Gets and displays a form to update an ad

        Args:
            request (HttpRequest): The current request
            pk (int): The primary key of the ad to be updated

        Returns:
            HttpResponse: The response filled with the form
        """
        ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(instance=ad)
        context = {"form": form}
        return render(request, template_name=self.template_name, context=context)

    def post(self, request, pk: int = None):
        """Posts the updated ad information

        Args:
            request (HttpRequest): The current request
            pk (int, optional): The primary key of the ad to be updated

        Returns:
            (HttpResponse | HttpResponseRedirect): The response filled with the form if there was an error, or a redirected response if it was successful
        """
        ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=ad)

        # If there are errors
        if not form.is_valid():
            context = {"form": form}
            return render(request, template_name=self.template_name, context=context)

        ad = form.save(commit=False)
        ad.save()

        return redirect(self.success_url)


class AdDeleteView(OwnerDeleteView):
    model = Ad


def stream_file(request, pk: int) -> HttpResponse:
    """Displays the ad picture

    Args:
        pk (int): The primary key of the ad

    Returns:
        HttpResponse: The page displaying the picture
    """
    ad = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response["Content-Type"] = ad.content_type
    response["Content-Length"] = len(ad.picture)
    response.write(ad.picture)
    return response


#################
# Comment Views #
#################


class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        """Posts the comment

        Args:
            request (HttpRequest): The current request
            pk (int, optional): The primary key of the ad

        Returns:
            (HttpResponseRedirect | HttpResponsePermanentRedirect): A redirect to the ad page
        """
        ad = get_object_or_404(Ad, id=pk)
        comment = Comment(text=request.POST["comment"], owner=request.user, ad=ad)
        comment.save()
        return redirect(reverse("ads:ad_detail", args=[pk]))


class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "ads/comment_delete.html"

    def get_success_url(self) -> str:
        ad = self.object.ad
        return reverse("ads:ad_detail", args=[ad.id])


#################
# Favorites Views #
#################


@method_decorator(csrf_exempt, name="dispatch")
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        ad = get_object_or_404(Ad, id=pk)
        fav = Fav(user=request.user, ad=ad)
        try:
            fav.save()  # In case of duplicates
        except IntegrityError as error:
            pass
        return HttpResponse()


@method_decorator(csrf_exempt, name="dispatch")
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        ad = get_object_or_404(Ad, id=pk)

        try:
            Fav.objects.get(user=request.user, ad=ad).delete()
        except Fav.DoesNotExist as error:
            pass
        return HttpResponse()