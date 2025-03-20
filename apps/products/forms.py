from django import forms
from .models import Product

# ModelForm for Product to be used in posting products
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'category', 'image']
