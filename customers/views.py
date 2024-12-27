from django.utils.timezone import now, timedelta
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Customer, JWTToken, Payment, User
from .serializers import CustomerSerializer, PaymentSerializer, UserSerializer


class UserView(APIView):
    def get(self, request, *args, **kwargs):
        """Retrieve all users"""
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """Create a new user"""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    """
    Handle user login and token generation
    """

    def post(self, request, *args, **kwargs):
        """
        Authenticate user and return access & refresh tokens
        """
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                return Response(
                    {"error": "Account is disabled."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            expires_at = now() + timedelta(
                seconds=refresh.access_token.lifetime.total_seconds()
            )

            # Save the token in the database
            JWTToken.objects.update_or_create(
                user=user,
                defaults={
                    "token": access_token,
                    "expires_at": expires_at,
                },
            )

            return Response(
                {
                    "refresh": str(refresh),
                    "access": access_token,
                    "user": {
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Invalid email or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class TokenAuthenticationAPIView(APIView):
    """
    APIView to handle token authentication.
    """

    def get(self, request, *args, **kwargs):
        """
        Check if the provided token is valid.
        """
        token = kwargs.get("token")
        if not token:
            return Response(
                {"error": "error", "message": "Token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            # Fetch the JWTToken instance matching the provided token
            jwt = JWTToken.objects.filter(token=token)
            if not jwt:
                return Response(
                    {"error": "error", "message": "Token not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            print("****jwt****")
            jwt = jwt.first()
            # Check if the token is valid based on the expiration time
            if jwt.expires_at > now():
                user = jwt.user
                user_data = {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
                return Response(
                    {
                        "status": "success",
                        "message": "Authenticated",
                        "user": user_data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                print("****jwt****")    
                return Response(
                    {"error": "error", "message": "Token expired"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except Exception as e:
            return Response(
                {"error": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CustomerView(APIView):
    def get(self, request, *args, **kwargs):
        """Retrieve all customers"""
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """Create a new customer"""
        request.data["payment"] = []
        request.data["total_amount"] = 0
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentView(APIView):
    def get(self, request, *args, **kwargs):
        """Retrieve all payments for a specific customer"""
        customer_id = kwargs.get("customer_id")
        try:
            payments = Payment.objects.filter(customer_id=customer_id).order_by("-date")
            serializer = PaymentSerializer(payments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response(
                {"error": "No payments found for this customer."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request, *args, **kwargs):
        """Create a new payment"""
        request.data["customer"] = kwargs.get("customer_id")
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            customer = Customer.objects.filter(id=kwargs.get("customer_id")).first()
            customer.total_amount = customer.total_amount + request.data["amount"]
            customer.save()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
