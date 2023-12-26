from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CharField
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Profile(AbstractUser):
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    fullName = models.CharField(max_length=200, db_index=True)
    email = models.EmailField(null=True, unique=True)
    phone = PhoneNumberField(null=True, blank=False, unique=True)

    def __str__(self) -> CharField:
        return self.fullName


def profile_preview_directory_path(instance: "UserAvatar", filename: str) -> str:
    return "profiles/profile_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename
    )


class UserAvatar(models.Model):
    src = models.ImageField(upload_to=profile_preview_directory_path, null=True)
    alt = models.CharField(max_length=100, null=True, blank=True)
    avatar = models.OneToOneField(
        Profile, null=True,
        on_delete=models.CASCADE,
        related_name='avatar'
    )


class Catalog(models.Model):
    class Meta:
        ordering = ['id']

    name = models.CharField(max_length=40)
    currentPage = models.SmallIntegerField(default=1)
    lastPage = models.SmallIntegerField(default=2)

    def __str__(self) -> str:
        return f"Catalog - {self.pk}"


def category_image_directory_path(instance: 'Category', filename: str):
    return "categories/category_{pk}/avatar/{filename}".format(
        pk=instance.pk,
        filename=filename
    )


class Category(models.Model):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    title = models.CharField(max_length=40)
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=category_image_directory_path
    )

    def get_image(self):
        image = {
            'src': self.image.url,
            'alt': self.image.name,
        }
        return image

    def __str__(self) -> str:
        return f"{self.title}"


class Subcategory(models.Model):
    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'

    title = models.CharField(max_length=40)
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=category_image_directory_path
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        verbose_name='подкатегория товаров',
        null=True
    )

    def get_image(self):
        image = {
            'src': self.image.url,
            'alt': self.image.name,
        }
        return image

    def __str__(self) -> str:
        return f"{self.title}"


class Tag(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self) -> str:
        return f"{self.name}"


class Specification(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    value = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.name}: {self.value}"


class Item(models.Model):
    catalog = models.ForeignKey(
        Catalog, verbose_name='каталог',
        on_delete=models.CASCADE,
        related_name='items'
    )
    category = models.ForeignKey(
        Category, verbose_name='категория',
        on_delete=models.CASCADE,
        related_name='cat_items'
    )
    subcategory = models.ForeignKey(
        Subcategory, verbose_name='подкатегория',
        on_delete=models.CASCADE,
        related_name='subcat_items'
    )
    price = models.DecimalField(
        default=0, max_digits=8,
        decimal_places=2
    )
    count = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    title = models.CharField(
        max_length=200, db_index=True,
        verbose_name='Название продукта'
    )
    description = models.TextField(blank=True, null=False)
    fullDescription = models.TextField(blank=True, db_index=True)
    freeDelivery = models.BooleanField(default=False)

    tags = models.ManyToManyField(Tag, blank=True, related_name='tags')
    specifications = models.ManyToManyField(
        Specification, blank=True,
        related_name='item_specifications'
    )
    rating = models.DecimalField(
        default=0.00, max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )

    salePrice = models.DecimalField(default=1, max_digits=8, decimal_places=2)
    dateFrom = models.DateField(null=True, blank=True)
    dateTo = models.DateField(null=True, blank=True)
    limited = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def get_rating(self):
        reviews = Review.objects.filter(item_id=self.pk).values_list(
            'rate', flat=True
        )
        if reviews.count() == 0:
            rating = 0
            return rating
        rating = sum(reviews) / reviews.count()
        return rating

    def __str__(self):
        return self.title


def item_images_directory_path(instance: "ItemImage", filename: str) -> str:
    return "products/products_{pk}/image/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class ItemImage(models.Model):
    src = models.ImageField(upload_to=item_images_directory_path)
    alt = models.CharField(max_length=100, null=True, blank=True)
    item = models.ForeignKey(
        Item, null=True,
        blank=True, on_delete=models.CASCADE,
        related_name="images"
    )


class Review(models.Model):
    author = models.ForeignKey(
        Profile, on_delete=models.CASCADE,
        related_name='author_review'
    )
    email = models.EmailField()
    text = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    rate = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='Оценка'
    )
    item = models.ForeignKey(
        Item, verbose_name="Продукт",
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    def __str__(self) -> str:
        return f"Review(pk={self.pk}, author={self.author!r})"


class Basket(models.Model):
    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE,
        related_name="baskets"
    )

    def __str__(self):
        return f'Basket of user {self.profile.fullName}'


class BasketItem(models.Model):
    basket = models.ForeignKey(
        Basket, on_delete=models.CASCADE,
        related_name="basket_items"
    )
    item = models.ForeignKey(
        Item, null=True,
        blank=True, on_delete=models.CASCADE,
        related_name="basket_items"
    )
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.quantity} x {self.item.title}'

