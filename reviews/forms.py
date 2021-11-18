from django import forms

from reviews.models import Review


class ReviewForm(forms.ModelForm):
    review = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Review
        fields = [
            'review',
            'rating',
            'image',
        ]


