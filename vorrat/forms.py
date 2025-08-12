from django import forms
from .models import FoodItem

class FoodItemForm(forms.ModelForm):
    expiration_date = forms.DateField(
        input_formats=['%d.%m.%Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    class Meta:
        model = FoodItem
        fields = ['name', 'quantity', 'expiration_date']
        labels = {
            'name': 'Name',
            'quantity': 'Anzahl',
            'expiration_date': 'Mindesthaltbarkeitsdatum'
        }
