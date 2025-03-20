from django import forms
from .models import RefundRequest

class RefundRequestForm(forms.ModelForm):
    class Meta:
        model = RefundRequest
        fields = ['reason', 'amount']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'})
        }

class AdminRefundResponseForm(forms.ModelForm):
    class Meta:
        model = RefundRequest
        fields = ['admin_notes']
        widgets = {
            'admin_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'})
        }