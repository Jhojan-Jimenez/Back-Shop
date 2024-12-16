from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from apps.product.models import Product
from apps.reviews.serializers import ReviewSerializer
from core.views import AuthenticatedAPIView, CustomAPIView
from .models import Review
from apps.orders.models import OrderItem
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from drf_spectacular.types import OpenApiTypes


class GetProductReviewsView(CustomAPIView):
    @extend_schema(
        description="Get all reviews for a product",
        responses={200:  ReviewSerializer(many=True),
                   404: {

            "type": "object",
            "properties": {
                    "error": {"type": "string"}
            },
            "example": [
                {"error": "Product ID must be an integer"},
                {"error": "This product does not exist"}
            ]

        },
            **CustomAPIView.get_500_errors(),
        },
    )
    def get(self, request, productId, format=None):
        try:
            product_id = int(productId)
        except:
            return Response(
                {'error': 'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            if not Product.objects.filter(id=product_id).exists():
                return Response(
                    {'error': 'This product does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )

            product = Product.objects.get(id=product_id)

            results = []

            if Review.objects.filter(product=product).exists():
                reviews = Review.objects.order_by(
                    '-date_created'
                ).filter(product=product)

                for review in reviews:
                    item = {}

                    item['id'] = review.id
                    item['rating'] = review.rating
                    item['comment'] = review.comment
                    item['date_created'] = review.date_created
                    item['user'] = review.user.first_name

                    results.append(item)

            return Response(
                {'reviews': results},
                status=status.HTTP_200_OK
            )

        except:
            return Response(
                {'error': 'Something went wrong when retrieving reviews'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetProductReviewView(CustomAPIView):
    @extend_schema(
        description="Get review for a product",
        responses={200:  ReviewSerializer,
                   404: {

                       "type": "object",
                       "properties": {
                               "error": {"type": "string"}
                       },
                       "example": [
                           {"error": "Product ID must be an integer"},
                           {"error": "This product does not exist"}
                       ]

                   },
                   **CustomAPIView.get_500_errors(),
                   },
    )
    def get(self, request, productId, format=None):
        user = self.request.user

        try:
            product_id = int(productId)
        except:
            return Response(
                {'error': 'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            if not Product.objects.filter(id=product_id).exists():
                return Response(
                    {'error': 'This product does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )

            product = Product.objects.get(id=product_id)

            result = {}

            if Review.objects.filter(user=user, product=product).exists():
                review = Review.objects.get(user=user, product=product)

                result['id'] = review.id
                result['rating'] = review.rating
                result['comment'] = review.comment
                result['date_created'] = review.date_created
                result['user'] = review.user.first_name

            return Response(
                {'review': result},
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                {'error': 'Something went wrong when retrieving review'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreateProductReviewView(AuthenticatedAPIView):
    @extend_schema(
        description="Create a review for a product. Only users who have purchased the product can leave a review.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "rating": {
                        "type": "number",
                        "format": "float",
                        "description": "The rating for the product (decimal value).",
                        "example": 4.5
                    },
                    "comment": {
                        "type": "string",
                        "description": "The comment for the review.",
                        "example": "Excellent product! Highly recommend it."
                    }
                },
                "required": ["rating", "comment"]
            }
        },
        responses={
            201: inline_serializer(
                name="ReviewResponse",
                fields={
                    "result": ReviewSerializer(),
                    "reviews": ReviewSerializer(many=True)
                },
            ),
            400: {

                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                },
                "example": [
                    {"error": "Rating must be a decimal value"},
                    {"error": "Must pass a comment when creating review"},
                    {"error": "You must have purchased this product to review it"}
                ]

            },
            **AuthenticatedAPIView.get_auth_responses(),
            404: {

                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                },
                "example":
                    {"error": "This Product does not exist"}


            },
            409: {

                    "type": "object",
                            "properties": {
                                "error": {"type": "string"}
                            },
                "example":
                    {"error": "Review for this course already created"}


            },
            **AuthenticatedAPIView.get_500_errors()
        }
    )
    def post(self, request, productId, format=None):
        user = self.request.user
        data = self.request.data

        try:
            rating = float(data['rating'])
        except:
            return Response(
                {'error': 'Rating must be a decimal value'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            comment = str(data['comment'])
        except:
            return Response(
                {'error': 'Must pass a comment when creating review'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if not Product.objects.filter(id=productId).exists():
                return Response(
                    {'error': 'This Product does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )

            product = Product.objects.get(id=productId)
            if not OrderItem.objects.filter(order__user=user, product_id=productId).exists():
                return Response(
                    {'error': 'You must have purchased this product to review it'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = {}
            results = []

            if Review.objects.filter(user=user, product=product).exists():
                return Response(
                    {'error': 'Review for this course already created'},
                    status=status.HTTP_409_CONFLICT
                )

            review = Review.objects.create(
                user=user,
                product=product,
                rating=rating,
                comment=comment
            )

            if Review.objects.filter(user=user, product=product).exists():
                result['id'] = review.id
                result['rating'] = review.rating
                result['comment'] = review.comment
                result['date_created'] = review.date_created
                result['user'] = review.user.first_name

                reviews = Review.objects.order_by('-date_created').filter(
                    product=product
                )

                for review in reviews:
                    item = {}

                    item['id'] = review.id
                    item['rating'] = review.rating
                    item['comment'] = review.comment
                    item['date_created'] = review.date_created
                    item['user'] = review.user.first_name

                    results.append(item)

            return Response(
                {'review': result, 'reviews': results},
                status=status.HTTP_201_CREATED
            )
        except:
            return Response(
                {'error': 'Something went wrong when creating review'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateProductReviewView(AuthenticatedAPIView):
    @extend_schema(
        description="Update a review for a product.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "rating": {
                        "type": "number",
                        "format": "float",
                        "description": "The rating for the product (decimal value).",
                        "example": 4.5
                    },
                    "comment": {
                        "type": "string",
                        "description": "The comment for the review.",
                        "example": "Excellent product! Highly recommend it."
                    }
                }
            }
        },
        responses={
            201: inline_serializer(
                name="ReviewResponse",
                fields={
                    "result": ReviewSerializer(),
                    "reviews": ReviewSerializer(many=True)
                },
            ),
            400: {

                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                },
                "example": [
                    {"error": "Rating must be a decimal value"},
                    {"error": "Must pass a comment when creating review"},
                    {"error": "You must have purchased this product to review it"}
                ]

            },
            **AuthenticatedAPIView.get_auth_responses(),
            404: {

                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                },
                "example":
                    [{"error": "This Product does not exist"}, {
                        "error": "Review for this product does not exist"}]


            },
            409: {

                    "type": "object",
                            "properties": {
                                "error": {"type": "string"}
                            },
                "example":
                    {"error": "Review for this course already created"}


            },
            **AuthenticatedAPIView.get_500_errors()
        }
    )
    def put(self, request, productId, format=None):
        user = self.request.user
        data = self.request.data

        try:
            product_id = int(productId)
        except:
            return Response(
                {'error': 'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            rating = float(data['rating'])
        except:
            return Response(
                {'error': 'Rating must be a decimal value'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            comment = str(data['comment'])
        except:
            return Response(
                {'error': 'Must pass a comment when creating review'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if not Product.objects.filter(id=product_id).exists():
                return Response(
                    {'error': 'This product does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )

            product = Product.objects.get(id=product_id)

            result = {}
            results = []

            if not Review.objects.filter(user=user, product=product).exists():
                return Response(
                    {'error': 'Review for this product does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if Review.objects.filter(user=user, product=product).exists():

                review = Review.objects.filter(
                    user=user, product=product).first()

                if review:
                    review.rating = rating
                    review.comment = comment
                    review.save()

                review = Review.objects.get(user=user, product=product)

                result['id'] = review.id
                result['rating'] = review.rating
                result['comment'] = review.comment
                result['date_created'] = review.date_created
                result['user'] = review.user.first_name

                reviews = Review.objects.order_by('-date_created').filter(
                    product=product
                )

                for review in reviews:
                    item = {}

                    item['id'] = review.id
                    item['rating'] = review.rating
                    item['comment'] = review.comment
                    item['date_created'] = review.date_created
                    item['user'] = review.user.first_name

                    results.append(item)

            return Response(
                {'review': result, 'reviews': results},
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                {'error': 'Something went wrong when updating review'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteProductReviewView(AuthenticatedAPIView):
    @extend_schema(
        description="Get review for a product",
        responses={200:  ReviewSerializer(many=True),
                   **AuthenticatedAPIView.get_auth_responses(),
                   404: {

            "type": "object",
            "properties": {
                "error": {"type": "string"}
            },
                       "example": [
                           {"error": "Product ID must be an integer"},
                           {"error": "This product does not exist"},
                           {'error': 'Review for this product does not exist'}
            ]

        },
            **AuthenticatedAPIView.get_500_errors(),
        },
    )
    def delete(self, request, productId, format=None):
        user = self.request.user

        try:
            product_id = int(productId)
        except:
            return Response(
                {'error': 'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            if not Product.objects.filter(id=product_id).exists():
                return Response(
                    {'error': 'This product does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )

            product = Product.objects.get(id=product_id)

            results = []

            if Review.objects.filter(user=user, product=product).exists():
                Review.objects.filter(user=user, product=product).delete()

                reviews = Review.objects.order_by('-date_created').filter(
                    product=product
                )

                for review in reviews:
                    item = {}

                    item['id'] = review.id
                    item['rating'] = review.rating
                    item['comment'] = review.comment
                    item['date_created'] = review.date_created
                    item['user'] = review.user.first_name

                    results.append(item)

                return Response(
                    {'reviews': results},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Review for this product does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except:
            return Response(
                {'error': 'Something went wrong when deleting product review'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FilterProductReviewsView(AuthenticatedAPIView):
    @extend_schema(exclude=True)
    def get(self, request, productId, format=None):
        try:
            product_id = int(productId)
        except:
            return Response(
                {'error': 'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not Product.objects.filter(id=product_id).exists():
            return Response(
                {'error': 'This product does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        product = Product.objects.get(id=product_id)

        rating = request.query_params.get('rating')

        try:
            rating = float(rating)
        except:
            return Response(
                {'error': 'Rating must be a decimal value'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if not rating:
                rating = 5.0
            elif rating > 5.0:
                rating = 5.0
            elif rating < 0.5:
                rating = 0.5

            results = []

            if Review.objects.filter(product=product).exists():
                if rating == 0.5:
                    reviews = Review.objects.order_by('-date_created').filter(
                        rating=rating, product=product
                    )
                else:
                    reviews = Review.objects.order_by('-date_created').filter(
                        rating__lte=rating,
                        product=product
                    ).filter(
                        rating__gte=(rating - 0.5),
                        product=product
                    )

                for review in reviews:
                    item = {}

                    item['id'] = review.id
                    item['rating'] = review.rating
                    item['comment'] = review.comment
                    item['date_created'] = review.date_created
                    item['user'] = review.user.first_name

                    results.append(item)

            return Response(
                {'reviews': results},
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                {'error': 'Something went wrong when filtering reviews for product'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
