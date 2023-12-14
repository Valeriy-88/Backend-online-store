from django.contrib import admin

from .models import Profile, Item, Review, ItemImage, Specification, Tag, Category


class ItemInline(admin.StackedInline):
    model = ItemImage


class SpecificationInline(admin.TabularInline):
    model = Item.specifications.through


class TagInline(admin.TabularInline):
    model = Item.tags.through


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = "pk", "fullName", "username", "email", "phone"
    list_display_links = "pk", "fullName", "username"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'pk', 'name',
    list_display_links = 'pk', 'name',


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    inlines = [
        TagInline,
        SpecificationInline,
        ItemInline,
    ]
    list_display = "pk", "title", "price", "category", "count", "date"
    list_display_links = "pk", "title"


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = 'pk', 'src', 'alt'
    list_display_links = "pk",


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
    list_display = "pk", "author", "email", "rate"
    list_display_links = "pk", "author"

    def get_queryset(self, request):
        return Review.objects.select_related('item')


# class SubcategoryAdmin(admin.ModelAdmin):
#     list_display = "item",
#
#
# admin.site.register(Subcategory, SubcategoryAdmin)


# class OrderAdmin(admin.ModelAdmin):
#     list_display = "", "", "", "", "", ""
#     list_filter = "", "",
#
#
# admin.site.register(Order, OrderAdmin)

