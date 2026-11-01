from product.models import Product
from product.serializers import ProductSerializer
from rest_framework.viewsets import ModelViewSet


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.all()