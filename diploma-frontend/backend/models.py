from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Catalog(models.Model):
    currentPage = models.SmallIntegerField(default=1)
    lastPage = models.SmallIntegerField(default=2)


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
    silePrice = models.DecimalField(default=1, max_digits=8, decimal_places=2)
    dateFrom = models.DateField(null=True, blank=True)
    dateTo = models.DateField(null=True, blank=True)
    catalog = models.ForeignKey(Catalog, verbose_name='каталог', on_delete=models.CASCADE, related_name='products')


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


class Review(models.Model):
    author = models.CharField(max_length=100, db_index=True)
    email = models.EmailField()
    text = models.TextField(max_length=5000)
    rate = models.SmallIntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)
    product = models.ForeignKey(Product, verbose_name="продукт", on_delete=models.CASCADE, related_name="reviews")


def profile_preview_directory_path(instance: "Profile", filename: str) -> str:
    return "profiles/profile_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class Profile(AbstractUser):
    fullName = models.CharField(max_length=200, db_index=True)
    email = models.EmailField(null=True, unique=True)
    phone = PhoneNumberField(null=True, blank=False, unique=True)
    avatar = models.ImageField(null=True, blank=True, upload_to=profile_preview_directory_path)

    def __str__(self):
        return self.username
