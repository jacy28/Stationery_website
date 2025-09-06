from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.validators import RegexValidator


# Create your models here.
class Stationery(models.Model):
    image=models.ImageField(upload_to='stationeries/')
    name=models.CharField(max_length=200)
    desc=models.TextField()

    def __str__(self):
        return  self.name
    
class FeaturedProduct(models.Model):
    image=models.ImageField(upload_to='featured/')
    name=models.CharField(max_length=200)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    offer_price=models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.price}"
    
class TrendingProduct(models.Model):
    image=models.ImageField(upload_to='trending/')

    def __str__(self):
        return str(self.image)
    
class SchoolProduct(models.Model):
    image=models.ImageField(upload_to='school_products/')
    name=models.CharField(max_length=200)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    offer_price=models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.price}"
    
class TeamMember(models.Model):
    photo=models.ImageField(upload_to='team/')
    name=models.CharField(max_length=100)
    role=models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.role}"
    
class Category(models.Model):
    name=models.CharField(max_length=200)
    banner=models.ImageField(upload_to='banner_images/')

    def __str__(self):
        return self.name

class Product(models.Model):
    category=models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    image=models.ImageField(upload_to='products/')
    name=models.CharField(max_length=200)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    offer_price=models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    
class PriceRange(models.Model):
    label=models.CharField(max_length=50)
    min_price=models.DecimalField(max_digits=8, decimal_places=2)
    max_price=models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.label


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'product')  # ensures one cart entry per product per user

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

    @property
    def total_price(self):
        if self.quantity >= 3:
            sets_of_three = self.quantity // 3
            remaining = self.quantity % 3
            total = sets_of_three * Decimal(self.product.offer_price) + remaining * Decimal(self.product.price)
        else:
            total = self.quantity * Decimal(self.product.price)
        return total

    
    @property
    def total_price_display(self):
        return f"{self.total_price:.2f}"


class AboutSection(models.Model):
    title=models.CharField(max_length=200)
    desc=models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
    
class AboutSectionImage(models.Model):
    section=models.ForeignKey(AboutSection, on_delete=models.CASCADE, related_name="images")
    image=models.ImageField(upload_to='section_images/')

    def __str__(self):
        return self.section.title
    
class ContactInfo(models.Model):
    icon=models.CharField(max_length=50, help_text="Bootstrap icon class, e.g. bi-geo-alt")
    title=models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
    
class PhoneNumber(models.Model):
    contact=models.ForeignKey(ContactInfo, on_delete=models.CASCADE, related_name='phones')
    number=models.CharField(max_length=20)

    def __str__(self):
        return self.number
    
class EmailAddress(models.Model):
    contact = models.ForeignKey(ContactInfo, on_delete=models.CASCADE, related_name="emails")
    email = models.EmailField()

    def __str__(self):
        return self.email
    
class ContactMessage(models.Model):
    name=models.CharField(max_length=200)
    email=models.EmailField()
    phone=models.CharField(max_length=15)
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
    
postal_code_validator = RegexValidator(
    regex=r'^\d{6}$',
    message='Postal code must be exactly 6 digits.'
)

class BillingDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="billings", null=True, blank=True)
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=255)
    code = models.CharField(max_length=6, validators=[postal_code_validator])

    def __str__(self):
        return self.name    
    
class PaymentMethod(models.Model):
    name=models.CharField(max_length=100)
    icon=models.ImageField(upload_to='payment_icons/', blank=True, null=True)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", null=True, blank=True)
    billing = models.ForeignKey(BillingDetails, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),           
        ("Shipped", "Shipped"),
        ("Out for Delivery", "Out for Delivery"),  
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),

    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")

    def __str__(self):
        return f"Order #{self.id} - {self.billing.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Automatically calculate subtotal
        self.subtotal = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"