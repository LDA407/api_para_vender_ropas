from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import permissions
from product.models import Product
from product.serializers import ProductSerializer
from .models import Review
from backend.utils.responses import *


class GetProductReviewView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request, productId, format=None):
        try: product_id = int(productId)
        except ValueError:
            return bad_request({'error': 'The ID must be an integer'})
        
        try:
            if not Product.products._exists(product_id):
                return not_found({'error': f'The product with id {product_id} does not exist'})

            product = Product.objects.get(id = product_id)
            result = []
            if Review.objects.filter(product=product).exists():
                reviews = Review.objects.get(product=product)
                for review in reviews:
                    product = Product.objects.get(id=review.product.id)
                    product = ProductSerializer(product)
                    result.append({
                        'id': review.id,
                        'user': review.user.first_name,
                        'rating' : review.rating,
                        'comment' : review.comment,
                        'created_at' : review.created_at
                        
                    })
                return success_response({'cart': result})
        except Exception as error:
            return server_error({'error': f'{error}'})


class CreateProductReviewView(APIView):
    
    def post(self, request, productId, format=None):
        user = self.request.user
        data = self.request.data

        try: product_id = int(productId)
        except ValueError:
            return bad_request({'error': 'The ID must be an integer'})
        
        try:
            if not Product.products._exists(product_id):
                return not_found({'error': f'The product with id {product_id} does not exist'})

            product = Product.objects.get(id = product_id)
            result = []
            results = []

            if Review.objects.filter(user = user, product = product).exists():
                return conflict_response({'error': f'The review for this product already created'})
            
            review = Review.objects.create(
                user = data.get('user'),
                product = data.get('product'),
                rating = data.get('rating'),
                comment = data.get('comment')
            )

            if Review.objects.filter(user=user, product=product).exists():
                result.append({
                    'id'           : review.id,
                    'user'         : review.user.first_name,
                    'rating'       : review.rating,
                    'comment'      : review.comment,
                    'created_at'   : review.created_at
                })

                reviews = Review.objects.order_by('-created_at').filter(
                    product = product
                )
                for review in reviews:
                    results.append({
                        'id'           : review.id,
                        'user'         : review.user.first_name,
                        'rating'       : review.rating,
                        'comment'      : review.comment,
                        'created_at'   : review.created_at
                    })
            
            return success_response({'review': result, 'reviews': results})

        except Exception as error:
            return server_error({'error': f'{error}'})


class UpdateProductReviewView(APIView):
    
    def put(self, request, productId, format=None):
        user = self.request.user
        data = self.request.data

        try: product_id = int(productId)
        except ValueError:
            return bad_request({'error': 'The product ID must be an integer'})
        # ====================

        try: rating = float(data.get('rating'))
        except ValueError:
            return bad_request({'error': 'Rating must be a decimal value'})
        # ====================

        try: comment = str(data.get('comment'))
        except ValueError:
            return bad_request({'error': 'Must pass a comment when creating review'})
        # ====================
        
        try:
            if not Product.products._exists(product_id):
                return not_found({'error': f'The product with ID {product_id} does not exist'})
            
            product = Product.objects.get(id = product_id)

            if not Review.objects.filter(user = user, product = product).exists():
                return conflict_response({'error': 'The review for this product does not exist'})
            
            result = []
            results = []

            if Review.objects.filter(user=user, product=product).exists():
                result.append({
                    'id': review.id,
                    'user': review.user.first_name,
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at
                })

                reviews = Review.objects.order_by('-created_at').filter(
                    product=product
                )
                for review in reviews:
                    results.append({
                        'id': review.id,
                        'user': review.user.first_name,
                        'rating': review.rating,
                        'comment': review.comment,
                        'created_at': review.created_at
                    })

            return success_response({'review': result, 'reviews': results})
        except Exception as error:
            return server_error({'error': f'{error}'})


class DeleteProductReviewView(APIView):
    
    def delete(self, request, productId, format=None):
        user = self.request.user
        data = self.request.data

        try: product_id = int(productId)
        except ValueError:
            return bad_request({'error': 'The product ID must be an integer'})
        # ====================
        try:
            if not Product.products._exists(product_id):
                return not_found({'error': f'The product with ID {product_id} does not exist'})

            product = Product.objects.get(id=product_id)
            results = []

            if Review.objects.filter(user=user, product=product).exists():
                Review.objects.filter(user=user, product=product).delete()
                reviews = Review.objects.order_by('-created_at').filter(
                    product=product
                )
                for review in reviews:
                    results.append({
                        'id': review.id,
                        'user': review.user.first_name,
                        'rating': review.rating,
                        'comment': review.comment,
                        'created_at': review.created_at
                    })
                return success_response({'reviews': results})
            return not_found({'error': f'The review for this product does not exist'})
        except Exception as error:
            return server_error({'error': f'{error}'})


class FilterProductReviewView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, productId, format=None):
        user = self.request.user
        data = self.request.data

        try: product_id = int(productId)
        except ValueError:
            return bad_request({'error': 'The product ID must be an integer'})
        # ====================

        if not Product.products._exists(product_id):
            return not_found({'error': f'The product with ID {product_id} does not exist'})
        # ====================

        product = Product.objects.get(id=product_id)
        rating = request.query_params.get('rating')

        try: rating = float(data.get('rating'))
        except ValueError:
            return bad_request({'error': 'Rating must be a decimal value'})

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
                    reviews = Review.objects.order_by('-created_at').filter(
                        rating=rating, product=product
                    )
                else:
                    reviews = Review.objects.order_by('-created_at').filter(
                        rating__lte=rating, product=product
                    ).filter(rating__gte=(rating-0.5), product=product)
                
                for review in reviews:
                    results.append({
                        'id': review.id,
                        'user': review.user.first_name,
                        'rating': review.rating,
                        'comment': review.comment,
                        'created_at': review.created_at
                    })
                return success_response({'reviews': results})

        except Exception as error:
            return server_error({'error': f'{error}'})
