import json, random
from product.models import Product, Category
from django.shortcuts import get_object_or_404
filename ="C:\\Users\\LDA407\\PythonProjects\\ecommers_react\\backend\\utils\\product.json"


with open(filename, 'r', encoding="utf8") as f: 
    data = json.load(f)
    for item in data:
        p = Product.objects.create(
            name = item["title"],
            description = item["description"],
            price = item["price"],
            quantity=random.randint(50, 500),
            category = get_object_or_404(Category ,name=item["category"])
        )
        p.save()
