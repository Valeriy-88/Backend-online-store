from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Product(models.Model):
    category = models.SmallIntegerField(default=1)
    price = models.DecimalField(default=1, max_digits=8, decimal_places=2)
    count = models.SmallIntegerField(default=1)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    fullDescription = models.TextField(blank=True, db_index=True)
    freeDelivery = models.BooleanField(default=False)
    rating = models.DecimalField(default=0, max_digits=2, decimal_places=1)


class Specification(models.Model):
    name = models.CharField(max_length=40)
    value = models.CharField(max_length=40)
    product = models.ManyToManyField(Product, related_name='specifications')


class Tag(models.Model):
    name = models.CharField(max_length=40)
    product = models.ManyToManyField(Product, related_name='tags')


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,
        filename=filename,
    )


class ProductImage(models.Model):
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.CharField(max_length=200, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")


class Author(models.Model):
    author = models.CharField(max_length=100, db_index=True)
    email = models.EmailField()
    text = models.TextField(max_length=5000)
    rate = models.SmallIntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)
    product = models.ForeignKey(Product, verbose_name="продукт", on_delete=models.CASCADE, related_name="authors")


def profile_preview_directory_path(instance: "Profile", filename: str) -> str:
    return "profile/preview/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class Profile(AbstractUser):
    email = models.EmailField(null=True)
    phone = PhoneNumberField(null=True, blank=False, unique=True)
    avatar = models.ImageField(null=True, blank=True, upload_to=profile_preview_directory_path)

    def __str__(self):
        return self.username
