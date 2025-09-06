from django.contrib import admin
from .models import (
    Stationery, 
    FeaturedProduct, 
    TrendingProduct, 
    SchoolProduct, 
    TeamMember, 
    Category,
    Product,
    PriceRange,
    AboutSection, 
    AboutSectionImage, 
    ContactInfo,
    PhoneNumber,
    EmailAddress, PaymentMethod, Order
)

admin.site.register(Stationery)
admin.site.register(FeaturedProduct)
admin.site.register(TrendingProduct)    
admin.site.register(SchoolProduct)    
admin.site.register(TeamMember)
admin.site.register(PaymentMethod)

class AboutSectionImageInline(admin.TabularInline):  
    model = AboutSectionImage
    extra = 2  

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=("id", "name")
    search_fields=("name",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price")
    list_filter = ("category",)
    search_fields = ("name",)

@admin.register(PriceRange)
class PriceRangeAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "min_price", "max_price")
    search_fields = ("label",)

@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "desc")
    inlines = [AboutSectionImageInline]

class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber

class EmailAddressInline(admin.TabularInline):
    model = EmailAddress

@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ("title", "icon")
    inlines = [PhoneNumberInline, EmailAddressInline]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'billing', 'user', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    list_editable = ('status',)
    search_fields = ('billing__name', 'user__username', 'id')
    ordering = ('-created_at',)