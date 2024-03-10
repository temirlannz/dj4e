from typing import Any
from django import forms
from .models import Ad
from django.core.files.uploadedfile import InMemoryUploadedFile
from .humanize import natural_size


# Form to create/update an ad
class CreateForm(forms.ModelForm):
    max_upload_limit = 2 * 1024 * 1024
    max_upload_limit_text = natural_size(max_upload_limit)

    # Call this 'picture' so it gets copied from the form to the in-memory model
    # It will not be the "bytes", it will be the "InMemoryUploadedFile"
    # because we need to pull out things like content_type
    picture = forms.FileField(
        required=False, label="File to Upload <= " + max_upload_limit_text
    )
    upload_field_name = "picture"

    class Meta:
        model = Ad
        fields = ["title", "price", "text", "picture", "tags"]

    def clean(self) -> None:
        """Validate the size of the picture"""
        cleaned_data = super().clean()
        pic = cleaned_data.get("picture")
        if pic is None:
            return
        if len(pic) > self.max_upload_limit:
            self.add_error(
                "picture", "File must be < " + self.max_upload_limit_text + " bytes"
            )

    def save(self, commit: bool = True) -> Any:
        """Convert uploaded File object to a picture

        Args:
            commit (bool, optional): Whether the instance is going to be saved to the database or not. Defaults to True.

        Returns:
            Any: The model instance
        """
        instance = super(CreateForm, self).save(commit=False)

        # Only adjust picture if it is a freshly uploaded file
        f = instance.picture  # Make a copy
        if isinstance(f, InMemoryUploadedFile):
            bytearr = f.read()
            instance.content_type = f.content_type
            instance.picture = bytearr  # Overwrite with the actual image data

        if commit:
            instance.save()
            self.save_m2m()  # To save tags

        return instance


# Form to add a comment
class CommentForm(forms.Form):
    comment = forms.CharField(required=True, max_length=500, min_length=3, strip=True)