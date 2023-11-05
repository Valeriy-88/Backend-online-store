from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ProductSerializer, AuthorSerializer
from .models import Product


class ProductsListView(APIView):
    def get(self, request, id):
        product = Product.objects.filter(id=id)
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data, template_name="frontend/product.html")


class ReviewCreateView(APIView):
    def post(self, request, id):
        request.data['product'] = id
        review = AuthorSerializer(data=request.data)
        if review.is_valid():
            review.save()
        return Response(status=201)
