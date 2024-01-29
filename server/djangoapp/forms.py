from django import forms
from .models import DealerReview

class ReviewForm(forms.ModelForm):
    class Meta:
        model = DealerReview
        fields = ['name', 'purchase', 'review', 'purchase_date', 'car_make', 'car_model', 'car_year']