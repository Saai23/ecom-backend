from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Product, Cart, Order, CartProduct, OrderProduct
from .serializers import UserSerializer, ProductSerializer, CartSerializer, OrderSerializer, CartProductSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Login successful", "user": username}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CartView(generics.RetrieveUpdateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.cart

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        product = Product.objects.get(pk=pk)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product)
        cart_product.quantity += 1
        cart_product.save()
        return Response({"message": "Product added to cart"}, status=status.HTTP_200_OK)

class CheckoutView(APIView):
    def post(self, request):
        try:
            cart_data = request.data.get('cart')
            username = request.data.get('user')

            # Validate cart data format
            if not isinstance(cart_data, list):
                return Response({"error": "Invalid cart data format. Expected an array of products."}, status=status.HTTP_400_BAD_REQUEST)
            
            if len(cart_data) == 0:
                return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Example: Calculate total price and create order products
            total = 0
            order_products = []

            for item in cart_data:
                price = float(item.get('price', 0))
                quantity = int(item.get('quantity', 0))
                total += price * quantity
                
                order_products.append(OrderProduct(
                    product_id=item['id'],
                    quantity=quantity,
                    # Ensure to set the 'order' field correctly below
                ))

            # Fetch the user based on the username
            user = User.objects.get(username=username)

            # Create the order
            order = Order.objects.create(user=user, total=total)

            # Assign the order instance to each order product
            for op in order_products:
                op.order = order

            # Bulk create the order products
            OrderProduct.objects.bulk_create(order_products)

            return Response({"message": "Checkout successful"}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)