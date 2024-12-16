from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from core.views import CustomAPIView
from .serializers import ProductSerializer
from .models import Product
from apps.category.models import Category
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class ProductDetailView(CustomAPIView):
    @extend_schema(
        description="Get detail about one product",
        responses={
            200: ProductSerializer,
            404: {

                    "type": "object",
                            "properties": {
                                "error": {"type": "string"}
                            },
                "example": {"error": "Product with this ID does not exist"}

            },
            **CustomAPIView.get_500_errors()
        }
    )
    def get(self, request, productId, format=None):
        try:
            product_id = int(productId)
        except:
            return Response(
                {'error': 'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND)
        if Product.objects.filter(id=product_id).exists():
            product = Product.objects.get(id=product_id)

            product = ProductSerializer(product)

            return Response({'product': product.data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Product with this ID does not exist'},
                status=status.HTTP_404_NOT_FOUND)

# Products sort


class ListProductsView(CustomAPIView):
    def get(self, request, format=None):
        if Product.objects.all().exists():

            sortBy = request.GET.get('sortBy')

            if not (sortBy == 'date_created' or sortBy == 'price' or sortBy == 'sold' or sortBy == 'name'):
                sortBy = 'date_created'

            order = request.GET.get('order')
            limit = request.GET.get('limit')

            if not limit:
                limit = 12
            try:
                limit = int(limit)
            except:
                return Response(
                    {'error': 'Limit must be an integer'},
                    status=status.HTTP_404_NOT_FOUND)

            if order == 'desc':
                sortBy = '-' + sortBy
                products = Product.objects.order_by(sortBy).all()[:int(limit)]
            elif order == 'asc':
                products = Product.objects.order_by(sortBy).all()[:int(limit)]
            else:
                products = Product.objects.order_by(sortBy).all()

            products = ProductSerializer(products, many=True)

            if products:
                return Response({'products': products.data}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'No products to list'},
                    status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({'error': 'No productsfound'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Filter Products By category ID and search (Similar Strings in Name or Description)


class ListSearchView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        data = self.request.data

        try:
            category_id = int(data['category_id'])
        except:
            return Response(
                {'error': 'Category ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND)

        search = data['search']

        if len(search) == 0:
            search_results = Product.objects.order_by('-date_created').all()
        else:
            # Q clase para manejar consultas espaciales, en este caso que contengan en alguna parte el parametro search
            search_results = Product.objects.filter(
                Q(description__icontains=search) | Q(name__icontains=search)
            )

        if category_id == 0:
            search_results = ProductSerializer(search_results, many=True)
            return Response(
                {'search_products': search_results.data},
                status=status.HTTP_200_OK)

        if not Category.objects.filter(id=category_id).exists():
            return Response(
                {'error': 'Category not found'},
                status=status.HTTP_404_NOT_FOUND)

        category = Category.objects.get(id=category_id)

        if category.parent:
            search_results = search_results.filter(category=category)

        else:
            if not Category.objects.filter(parent=category).exists():
                search_results = search_results.filter(category=category)

            else:
                categories = Category.objects.filter(parent=category)
                filtered_categories = [category]

                for cat in categories:
                    filtered_categories.append(cat)

                filtered_categories = tuple(filtered_categories)

                search_results = search_results.filter(
                    category__in=filtered_categories)

        search_results = ProductSerializer(search_results, many=True)
        return Response({'search_products': search_results.data}, status=status.HTTP_200_OK)


# With an ID product, select it category and found products with the same category
class ListRelatedView(CustomAPIView):
    @extend_schema(
        description="Retrieve a list of related products for a specific product ID based on its category, Max 3 for request.",
        responses={
            200: ProductSerializer(many=True),
            404: {

                    "type": "object",
                    "properties": {
                        "error": {"type": "string"}
                    },
                "example": [{
                    "no_products":  {"error": "Product ID must be an integer"}},
                    {"invalid_limit":  {"error": "Product with this product ID does not exist"}
                     }]

            },
            **CustomAPIView.get_500_errors()
        }
    )
    def get(self, request, productId, format=None):
        try:
            product_id = int(productId)
        except:
            return Response(
                {'error': 'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND)

        if not Product.objects.filter(id=product_id).exists():
            return Response(
                {'error': 'Product with this product ID does not exist'},
                status=status.HTTP_404_NOT_FOUND)

        category = Product.objects.get(id=product_id).category

        if Product.objects.filter(category=category).exists():
            # Si la categoria tiene padrem filtrar solo por la categoria y no el padre tambien
            if category.parent:
                related_products = Product.objects.order_by(
                    '-sold'
                ).filter(category=category)
            else:
                if not Category.objects.filter(parent=category).exists():
                    related_products = Product.objects.order_by(
                        '-sold'
                    ).filter(category=category)

                else:
                    categories = Category.objects.filter(parent=category)
                    filtered_categories = [category]

                    for cat in categories:
                        filtered_categories.append(cat)

                    filtered_categories = tuple(filtered_categories)
                    related_products = Product.objects.order_by(
                        '-sold'
                    ).filter(category__in=filtered_categories)

            related_products = related_products.exclude(id=product_id)
            related_products = ProductSerializer(related_products, many=True)

            if len(related_products.data) > 3:
                return Response(
                    {'related_products': related_products.data[:3]},
                    status=status.HTTP_200_OK)
            elif len(related_products.data) > 0:
                return Response(
                    {'related_products': related_products.data},
                    status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'No related products found'},
                    status=status.HTTP_200_OK)

        else:
            return Response(
                {'error': 'No related products found'},
                status=status.HTTP_200_OK)

# Filter with cateogri, price range, sort and order


class ListBySearchView(CustomAPIView):
    @extend_schema(
        description="Filter and retrieve products based on category, price range, sorting, and search parameters.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "categoryId": {"type": "integer", "example": 0},
                    "priceRange": {"type": "string", "example": "100000 - 200000"},
                    "sortBy": {"type": "string", "enum": ["date_created"], "example": ["date_created", "price", "sold", "name", "rating"]},
                    "order": {"type": "string", "enum": ["asc"], "example": ["asc", "desc"]},
                    "search": {"type": "string", "description": "adidas"}
                },
                "required": ["categoryId"]
            }
        },
        responses={
            200: ProductSerializer(many=True),
            404: {

                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                },
                "example": [
                    {"invalid_category_id": {
                        "error": "Category ID must be an integer"}},
                    {"invalid_category": {
                        "error": "This category does not exist"}},
                    {"invalid_price_range": {
                        "error": "Invalid price range format"}}
                ]

            },
            **CustomAPIView.get_500_errors()
        }
    )
    def post(self, request, format=None):
        data = self.request.data

        try:
            category_id = int(data['categoryId'])
        except:
            return Response(
                {'error': 'Category ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND)

        price_range = data['priceRange']
        sort_by = data['sortBy']

        if not (sort_by == 'date_created' or sort_by == 'price' or sort_by == 'sold' or sort_by == 'name' or sort_by == 'rating'):
            sort_by = 'date_created'

        order = data['order']

        search = data['search']

        if len(search) == 0:
            product_results = Product.objects.all()
        else:
            # Q clase para manejar consultas espaciales, en este caso que contengan en alguna parte el parametro search
            product_results = Product.objects.filter(
                Q(description__icontains=search) | Q(name__icontains=search)
            )

        # Si categoryID es = 0, filtrar todas las categorias
        if category_id == 0:
            product_results = product_results.all()
        elif not Category.objects.filter(id=category_id).exists():
            return Response(
                {'error': 'This category does not exist'},
                status=status.HTTP_404_NOT_FOUND)
        else:
            category = Category.objects.get(id=category_id)
            if category.parent:
                # Si la categoria tiene padrem filtrar solo por la categoria y no el padre tambien
                product_results = product_results.filter(category=category)
            else:
                if not Category.objects.filter(parent=category).exists():
                    product_results = product_results.filter(category=category)
                else:
                    categories = Category.objects.filter(parent=category)
                    filtered_categories = [category]

                    for cat in categories:
                        filtered_categories.append(cat)

                    filtered_categories = tuple(filtered_categories)
                    product_results = product_results.filter(
                        category__in=filtered_categories)

        # Filtrar por precio
        if not price_range or not isinstance(price_range, str):
            product_results = product_results.all()

        else:
            price_range = price_range.split(" ")

            if len(price_range) > 1 and price_range[0] == "More":
                product_results = product_results.filter(
                    price__gte=int(price_range[2]))

            elif len(price_range) == 3 and price_range[1] == "-":
                product_results = product_results.filter(
                    price__gte=int(price_range[0]),
                    price__lt=int(price_range[2])
                )

            else:
                product_results = product_results.all()

        # Filtrar producto por sort_by
        if order == 'desc':
            sort_by = '-' + sort_by
            product_results = product_results.order_by(sort_by)
        elif order == 'asc':
            product_results = product_results.order_by(sort_by)
        else:
            product_results = product_results.order_by(sort_by)

        product_results = ProductSerializer(product_results, many=True)

        if len(product_results.data) > 0:
            return Response(
                {'filtered_products': product_results.data},
                status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'No products found'},
                status=status.HTTP_200_OK)
