from rest_framework import serializers

from order.models import Order
from product.serializers.product_serializer import Product, ProductSerializer

class OrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer(required=True, many=True)
    products_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, many=True)
    total = serializers.SerializerMethodField()

    def get_total(self, instance):
        total = sum([product.price for product in instance.product.all()])
        return total

    class Meta:
        model = Order
        fields = ['product', 'total', 'user', 'products_id']


    def create(self, validated_data):
        product_data = validated_data.pop('products_id')
        user_data = validated_data.pop('user')

        order = Order.objects.create(user=user_data)
        for product in product_data:
            order.product.add(product)    

        return order    