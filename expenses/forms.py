from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Expense, ExpenseCategory, Villa, ExpenseAllocation
import json


class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'اسم المستخدم',
            'email': 'البريد الإلكتروني',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المستخدم',
                'dir': 'rtl'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'البريد الإلكتروني',
                'dir': 'rtl'
            }),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'expense_type', 'category', 'title',
            'total_amount', 'date', 'supplier_name',
            'notes', 'invoice_image'
        ]
        widgets = {
            'expense_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_expense_type',
                'onchange': 'filterCategories(this.value)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_category'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: شراء أسمنت',
                'dir': 'rtl'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
                'id': 'id_total_amount',
                'onkeyup': 'recalculateAllocations()'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'supplier_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المورد (اختياري)',
                'dir': 'rtl'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية...',
                'dir': 'rtl'
            }),
            'invoice_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/gif,application/pdf'
            }),
        }
        labels = {
            'expense_type': 'نوع المصروف',
            'category': 'التصنيف',
            'title': 'العنوان',
            'total_amount': 'المبلغ الإجمالي',
            'date': 'التاريخ',
            'supplier_name': 'اسم المورد',
            'notes': 'ملاحظات',
            'invoice_image': 'صورة الفاتورة',
        }

    def clean_total_amount(self):
        amount = self.cleaned_data.get('total_amount')
        if amount is not None and amount <= 0:
            raise ValidationError('المبلغ يجب أن يكون أكبر من صفر.')
        return amount

    def clean(self):
        cleaned_data = super().clean()
        expense_type = cleaned_data.get('expense_type')
        category = cleaned_data.get('category')
        if expense_type and category:
            if category.category_type != expense_type:
                raise ValidationError(
                    'التصنيف المختار لا يتطابق مع نوع المصروف.'
                )
        return cleaned_data


class ExpenseFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'بحث... (عنوان، تصنيف، مورد، ملاحظات)',
            'dir': 'rtl'
        }),
        label='بحث'
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='من تاريخ'
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='إلى تاريخ'
    )
    expense_type = forms.ChoiceField(
        required=False,
        choices=[('', 'جميع الأنواع'), ('direct', 'مباشر'), ('indirect', 'غير مباشر')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='نوع المصروف'
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=ExpenseCategory.objects.all(),
        empty_label='جميع التصنيفات',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='التصنيف'
    )
    villa = forms.ModelChoiceField(
        required=False,
        queryset=Villa.objects.all(),
        empty_label='جميع الفيلات',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الفيلا'
    )
    supplier = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اسم المورد',
            'dir': 'rtl'
        }),
        label='المورد'
    )


class ReportFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='من تاريخ'
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='إلى تاريخ'
    )
    expense_type = forms.ChoiceField(
        required=False,
        choices=[('', 'جميع الأنواع'), ('direct', 'مباشر'), ('indirect', 'غير مباشر')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='نوع المصروف'
    )
