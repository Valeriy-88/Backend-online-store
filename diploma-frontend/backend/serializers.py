from rest_framework import serializers
from .models import (
    Item,
    Review,
    Specification,
    Tag,
    ItemImage,
    Profile,
    Catalog,
    Category,
    Subcategory,
    BasketItem,
    UserAvatar,
)


class AvatarUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAvatar
        fields = ['src', 'alt']


class PasswordUserSerializer(serializers.ModelSerializer):
    newPassword = serializers.CharField(max_length=200)

    class Meta:
        model = Profile
        fields = ['newPassword', 'password']

    def update(self, instance, validated_data):
        for newPassword in PasswordUserSerializer.Meta.fields: setattr(instance, newPassword,
                                                                       validated_data[newPassword])
        instance.set_password(validated_data['newPassword'])
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    avatar = AvatarUserSerializer()

    class Meta:
        model = Profile
        fields = ['username', 'fullName', 'password', 'email', 'phone', 'avatar']
        extra_kwargs = {'password': {'write_only': True}}
        depth = 1

    def create(self, validated_data):
        user = Profile(
            username=validated_data['username'],
            fullName=validated_data['fullName']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.fullName = validated_data.get('fullName', instance.fullName)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        exclude = ['id', 'item']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        exclude = ['id']


class ItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImage
        exclude = ['id', 'item']


class ReviewSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Review
        fields = '__all__'


class ReviewItemSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='fullName'
    )

    class Meta:
        model = Review
        fields = ['author', 'email', 'text', 'rate', 'date']


class ItemSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%A %B %d %Y %H:%M:%S")
    reviews = ReviewItemSerializer(many=True)
    images = ItemImageSerializer(many=True)
    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='id'
    )

    class Meta:
        model = Item
        exclude = ['subcategory', 'salePrice', 'dateFrom', 'dateTo', 'catalog', 'limited', 'active']
        depth = 1


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'name']


class CatalogMenuSerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'subcategories']
        depth = 1


class CatalogItemsSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%A %B %d %Y %H:%M:%S")
    reviews = ReviewSerializer(many=True)
    images = ItemImageSerializer(many=True)
    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='id'
    )
    tags = TagSerializer(many=True)

    class Meta:
        model = Item
        exclude = ['subcategory', 'dateFrom', 'dateTo', 'catalog', 'specifications']
        depth = 1

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        reviews = Review.objects.filter(item_id=instance.id).values_list(
            'rate', flat=True
        )
        tags = Tag.objects.filter(tags__id=instance.id)

        if reviews.count() == 0:
            rating = 'Нет отзывов'
        else:
            rating = sum(reviews) / reviews.count()

        representation['title'] = instance.title
        representation['price'] = instance.price
        representation['tags'] = [{'id': tag.pk, 'name': tag.name} for tag in tags]
        representation['reviews'] = reviews.count()
        representation['rating'] = rating
        return representation


class CatalogSerializer(serializers.ModelSerializer):
    items = CatalogItemsSerializer(many=True)

    class Meta:
        model = Catalog
        fields = ['items', 'currentPage', 'lastPage']


class BannerSerializer(CatalogItemsSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        tags = Tag.objects.filter(tags__id=instance.id)
        representation['tags'] = [tag.name for tag in tags]
        return representation


class SalesItemsSerializer(serializers.ModelSerializer):
    dateFrom = serializers.DateField(format="%m-%d")
    dateTo = serializers.DateField(format="%m-%d")
    images = ItemImageSerializer(many=True)

    class Meta:
        model = Item
        fields = ('id', 'price', 'salePrice', 'dateFrom', 'dateTo', 'title', 'images')
        depth = 1


class SalesSerializer(serializers.ModelSerializer):
    items = SalesItemsSerializer(many=True)

    class Meta:
        model = Catalog
        fields = ['items', 'currentPage', 'lastPage']


class BasketItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketItem
        fields = '__all__'

    def to_representation(self, instance):
        data = ItemSerializer(instance.item).data
        data['count'] = instance.quantity
        return data
