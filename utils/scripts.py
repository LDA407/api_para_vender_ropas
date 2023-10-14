import json, random
from apps.product.models import Product, Category
from django.shortcuts import get_object_or_404
filename ="/home/lda_pc/PythonProyects/api_para_vender_ropas/utils/products.json"
# C:\Users\LDA407\PythonProjects\ecommers_react\backend\utils\product.json

categories = '/home/lda_pc/PythonProyects/api_para_vender_ropas/utils/categories.json'
with open(categories, 'r', encoding="utf8") as f: 
    data = json.load(f)
    for item in data:
        c = Category.objects.create(
            name = item["name"]
        )
        c.save()


with open(filename, 'r', encoding="utf8") as f: 
    data = json.load(f)
    for item in data:
        p = Product.objects.create(
            name = item["name"],
            description = item["description"],
            price = item["price"],
            category = get_object_or_404(Category ,id=item["category"]),
            quantity=random.randint(50, 500),
            sold = item["sold"],
            date_created = item["date_created"]
        )
        p.save()