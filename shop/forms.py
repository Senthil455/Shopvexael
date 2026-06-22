from django import forms
from django.contrib.auth.models import User
from .models import Product, Category, SubCategory, Brand


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15, required=False)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken")
        return username


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    desc = forms.CharField(widget=forms.Textarea, max_length=1000)


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput, label="Current Password")
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm New Password")

    def clean_current_password(self):
        current = self.cleaned_data.get('current_password')
        if current and self.user and not self.user.check_password(current):
            raise forms.ValidationError("Current password is incorrect.")
        return current

    def clean_new_password(self):
        new = self.cleaned_data.get('new_password')
        if new and len(new) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if new and new.isnumeric():
            raise forms.ValidationError("Password cannot be entirely numeric.")
        return new

    def clean(self):
        cleaned_data = super().clean()
        new = cleaned_data.get('new_password')
        confirm = cleaned_data.get('confirm_password')
        if new and confirm and new != confirm:
            raise forms.ValidationError("New password and confirm password do not match.")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class CheckoutForm(forms.Form):
    address = forms.CharField(max_length=300)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    zipcode = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=15)
    payment = forms.CharField(max_length=100)


class SellerSignupForm(forms.Form):
    company_name = forms.CharField(max_length=200)
    description = forms.CharField(widget=forms.Textarea, required=False)


class SellerProductForm(forms.Form):
    name = forms.CharField(max_length=255)
    sku = forms.CharField(max_length=100, required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    subcategory = forms.ModelChoiceField(queryset=SubCategory.objects.all(), required=False)
    brand = forms.ModelChoiceField(queryset=Brand.objects.all(), required=False)
    short_description = forms.CharField(widget=forms.Textarea, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    discount_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    stock = forms.IntegerField(min_value=0)
    tags = forms.CharField(max_length=500, required=False)


class SellerSettingsForm(forms.Form):
    company_name = forms.CharField(max_length=200)
    description = forms.CharField(widget=forms.Textarea, required=False)
    email = forms.EmailField()
    full_name = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=15, required=False)


class ReviewForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)
    rating = forms.ChoiceField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
