from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings
from taggit.managers import TaggableManager


class Ad(models.Model):
    """
    Represents an ad.
    """

    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2, "Title must be greater than 2 characters")],
    )
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    text = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ad_owner"
    )
    comments = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="Comment", related_name="comments_owned"
    )

    # Picture information
    picture = models.BinaryField(null=True, editable=True)
    content_type = models.CharField(
        max_length=256, null=True, help_text="The MIMEType of the file"
    )

    # Favorites
    favorites = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="Fav", related_name="favorite_ads"
    )

    # Tags
    tags = TaggableManager(help_text="A comma-separated list of tags", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation of the model"""
        return self.title


class Comment(models.Model):
    """
    Represents a comment on an ad made by a certain user.
    """

    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters")]
    )
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ads_comments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation of the model"""
        if len(self.text) < 15:
            return self.text
        return self.text[:11] + " ..."


class Fav(models.Model):
    """
    Represents the relationship of a user liking an ad.
    """

    ad = models.ForeignKey("Ad", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("ad", "user")

    def __str__(self):
        """String representation of the model"""
        return "%s likes %s" % (self.user.username, self.ad.title[:10])