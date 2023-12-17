from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Catalog(models.Model):

    class Meta:
        ordering = ['id']

    currentPage = models.SmallIntegerField(default=1)
    lastPage = models.SmallIntegerField(default=2)

    def __str__(self) -> str:
        return f"Catalog - {self.pk}"


class Category(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self) -> str:
        return f"{self.name}"


class Item(models.Model):
    class Meta:
        ordering = ['id', 'rating', 'price', 'reviews', 'date']

    category = models.ForeignKey(Category, verbose_name='категории', on_delete=models.CASCADE, related_name='items')
    price = models.DecimalField(default=1, max_digits=8, decimal_places=2)
    count = models.SmallIntegerField(default=1)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    fullDescription = models.TextField(blank=True, db_index=True)
    freeDelivery = models.BooleanField(default=False)
    rating = models.DecimalField(default=0, max_digits=2, decimal_places=1)
    salePrice = models.DecimalField(default=1, max_digits=8, decimal_places=2)
    dateFrom = models.DateField(null=True, blank=True)
    dateTo = models.DateField(null=True, blank=True)
    catalog = models.ForeignKey(Catalog, verbose_name='каталог', on_delete=models.CASCADE, related_name='items')
    limited = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"Item(pk={self.pk}, name={self.title!r})"


class Subcategory(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='subcategories')


class Tag(models.Model):
    name = models.CharField(max_length=40)
    category = models.ForeignKey(Category, verbose_name='категории', on_delete=models.CASCADE, related_name='tags')
    item = models.ManyToManyField(Item, blank=True, related_name='tags')
    catalog = models.ForeignKey(Catalog, verbose_name='каталог', on_delete=models.CASCADE, related_name='tags')

    def __str__(self) -> str:
        return f"{self.name}"


class Specification(models.Model):
    name = models.CharField(max_length=40)
    value = models.CharField(max_length=40)
    item = models.ManyToManyField(Item, blank=True, related_name='specifications')

    def __str__(self) -> str:
        return f"{self.pk}: name={self.name!r}"


def item_images_directory_path(instance: "ItemImage", filename: str) -> str:
    return "products/images/{pk}/{filename}".format(
        pk=instance.item.pk,
        filename=filename,
    )


class ItemImage(models.Model):
    src = models.ImageField(upload_to=item_images_directory_path)
    alt = models.CharField(max_length=200, blank=True)
    item = models.ForeignKey(Item, null=True, blank=True, on_delete=models.CASCADE, related_name="images")


class Review(models.Model):
    author = models.CharField(max_length=100, db_index=True)
    email = models.EmailField()
    text = models.TextField(max_length=5000)
    rate = models.SmallIntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)
    item = models.ForeignKey(Item, verbose_name="продукт", on_delete=models.CASCADE, related_name="reviews")

    def __str__(self) -> str:
        return f"Review(pk={self.pk}, author={self.author!r})"


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

    def __str__(self) -> str:
        return f"Profile(pk={self.pk}, fullName={self.fullName!r})"

