from django.contrib import admin

from .models import (
    Profile, Item,
    Review, ItemImage,
    Specification,
    Tag, Category,
    Subcategory,
    Basket,
    BasketItem,
    Catalog, Order,
)


class BasketItemInline(admin.TabularInline):
    model = BasketItem


class ItemImageInline(admin.StackedInline):
    model = ItemImage


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = "pk", "fullName", "username", "email", "phone"
    list_display_links = "pk", "fullName", "username"


@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    list_display = 'pk', 'name'
    list_display_links = "pk", 'name'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'pk', 'title',
    list_display_links = 'pk', 'title',


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    inlines = [
        ItemImageInline,
    ]
    list_display = "pk", "title", "price", "category", "count", "date"
    list_display_links = "pk", "title"

    def get_queryset(self, request):
        return (
            Item.objects
            .prefetch_related(
                'category', 'subcategory',
                'tags', 'specifications',
                'catalog'
            )
        )


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = 'pk', 'src'
    list_display_links = "pk", 'src'

    def get_queryset(self, request):
        return ItemImage.objects.prefetch_related('item')


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = 'pk', 'name', 'value'
    list_display_links = "pk", 'name'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = 'pk', 'name',
    list_display_links = "pk", 'name'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = "pk", "author", "email",
    list_display_links = "pk", "author"

    def get_queryset(self, request):
        return Review.objects.prefetch_related('item', 'author')


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = 'pk', "title", 'category'
    list_display_links = "pk", "title"

    def get_queryset(self, request):
        return Subcategory.objects.prefetch_related('category')


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    inlines = [
        BasketItemInline,
    ]

    list_display = 'pk', 'profile'
    list_display_links = "pk", "profile"

    def get_queryset(self, request):
        return Basket.objects.prefetch_related('profile')


@admin.register(BasketItem)
class BasketItemAdmin(admin.ModelAdmin):
    list_display = 'pk', 'basket', 'item', 'quantity'
    list_display_links = "pk", "basket"

    def get_queryset(self, request):
        return BasketItem.objects.prefetch_related('basket', 'item')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = "pk", "profile", "address", "createdAt", "status"
    list_display_links = "pk", "profile",

    def get_queryset(self, request):
        return Order.objects.prefetch_related('items', 'profile', 'basket')
