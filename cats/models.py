from django.db import models
from django.core.validators import MinLengthValidator


class Breed(models.Model):
    name = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2, "Breed must be greater than 1 character")],
    )

    def __str__(self) -> str:
        """String that represents the Model object

        Returns:
            str: The name of the breed
        """
        return self.name


class Cat(models.Model):
    nickname = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2, "Nickname must be greater than 1 character")],
    )
    weight = models.PositiveIntegerField()
    foods = models.CharField(max_length=300)
    breed = models.ForeignKey(Breed, on_delete=models.CASCADE, null=False)

    def __str__(self) -> str:
        """String that represents the Model object

        Returns:
            str: The cat's nickname
        """
        return self.nickname
