from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.views import APIView
from rest_framework import permissions
from apps.product.models import Product
from .serializers import ReviewSerializer
from .models import Review
from utils.responses import *


class GetReview(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request, productId, format=None):
        try:
            product = get_object_or_404(Product, id = productId)
            if Review.objects.filter(product=product).exists():
                reviews = Review.objects.filter(product=product)
                serializer = list(ReviewSerializer(reviews, many = True).data)
                return success_response({'reviews': serializer})
            return not_content({'no result': "not reviews"})
        except Exception as error:
            return server_error({'error': f'{error}'})


class CreateReview(APIView):
    def post(self, request, productId, format=None):
        user = request.user
        data = request.data
        product = get_object_or_404(Product, id = productId)

        if Review.objects.filter(user=user, product=product).exists():
            return conflict_response({'error': f'A review for this product has already been created'})

        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user, product=product)
            review = serializer.data

            reviews = Review.objects.order_by('-created_at').filter(product=product)
            results = ReviewSerializer(reviews, many=True).data
            return created_response({'review': review, 'reviews': results})
        return bad_request(serializer.errors)


class UpdateReview(APIView):
    def put(self, request, productId, format=None):
        user = self.request.user
        data = self.request.data

        try: rating = float(data.get('rating'))
        except ValueError:
            return bad_request({'error': 'Rating must be a decimal value'})
        # ====================

        try: comment = str(data.get('comment'))
        except ValueError:
            return bad_request({'error': 'Must pass a comment when creating review'})
        # ====================
        
        try:
            product = get_object_or_404(Product, id = productId)
            if not Review.objects.filter(user = user, product = product).exists():
                return conflict_response({'error': 'The review for this product does not exist'})
            
            serializer = ReviewSerializer(rating = rating, comment = comment)
            if serializer.is_valid():
                serializer.save(user=user, product=product)
                review = serializer.data
                reviews = Review.objects.order_by('-created_at').filter(product=product)
                results = ReviewSerializer(reviews, many=True).data
                return created_response({'review': review, 'reviews': results})
            return not_content({'error': "no reviews"})
        except Exception as error:
            return server_error({'error': f'{error}'})


class DeleteReview(APIView):
    def delete(self, request, productId, format=None):
        product = get_object_or_404(Product, id = productId)
        review = get_object_or_404(Review, user = self.request.user, product=product)
        review.delete()

        reviews = Review.objects.order_by('-created_at').filter(product = product)
        results = ReviewSerializer(reviews, many = True).data
        return success_response({'reviews': results})


class FilterReview(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, productId, format=None):
        product = get_object_or_404(Product, id=productId)
        rating = request.query_params.get('rating', None)

        try:
            if rating:
                rating = float(rating)
                rating = max(min(rating, 5.0), 0.5)
            else:
                rating = 5.0
            
            reviews = Review.objects.filter(
                product=product, rating__gte=rating-0.5, rating__lte=rating
            ).order_by('-created_at')
            results = ReviewSerializer(reviews, many=True).data
            return success_response({'reviews': results})

        except Exception as error:
            return server_error({'error': f'{error}'})