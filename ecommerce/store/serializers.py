from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Cart, Order, CartProduct, OrderProduct

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id','name','description', 'price', 'stock',)

class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartProduct
        fields = ('id',)

class CartSerializer(serializers.ModelSerializer):
    products = CartProductSerializer(many=True, source='cartproduct_set')

    class Meta:
        model = Cart
        fields = ['id', 'user', 'products']

class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ('id',)

class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, source='orderproduct_set')

    class Meta:
        model = Order
        fields = ['id', 'user', 'products', 'total', 'created_at']