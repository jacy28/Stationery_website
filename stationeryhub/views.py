from django.shortcuts import render, redirect, get_object_or_404
from .models import (Stationery, FeaturedProduct, TrendingProduct, 
                     SchoolProduct, TeamMember, AboutSection,
                     ContactInfo, Category, Product, PriceRange, Cart, PaymentMethod, Order, OrderItem)
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import send_mail
from .forms import ContactForm, BillingForm
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.http import JsonResponse


# Create your views here.
def home(request):
    stationeries=Stationery.objects.all()
    featured_products=FeaturedProduct.objects.all()
    trending_products=TrendingProduct.objects.all()
    school_products=SchoolProduct.objects.all()
    team_members=TeamMember.objects.all()
    return render(request, 'home.html', {
        'stationeries':stationeries, 
        'featured_products':featured_products,
        'trending_products':trending_products,
        'school_products':school_products,
        'team_members':team_members
        })

def shop(request):
    categories=Category.objects.all()
    products=Product.objects.all()
    price_ranges=PriceRange.objects.all()

    # ---- Category Filter ----
    category_id=request.GET.get('category')
    selected_category=None

    if category_id:
        products=products.filter(category_id=category_id)
        try:
            selected_category=Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            selected_category=None
    else:
        try:
            selected_category=Category.objects.get(name="Office Basics")
            products=products.filter(category=selected_category)
        except Category.DoesNotExist:
            selected_category=None

    # Price Filter
    price_range_id=request.GET.get('price_range')
    selected_price_range=None
    if price_range_id:
        try:
            selected_price_range=PriceRange.objects.get(id=price_range_id)
            products=products.filter(
                price__gte=selected_price_range.min_price,
                price__lte=selected_price_range.max_price
            )
        except PriceRange.DoesNotExist:
            selected_price_range=None
            
    # ---- Pagination ----
    paginator = Paginator(products, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "categories": categories,
        "price_ranges": price_ranges,
        "products": page_obj,
        "selected_category": selected_category,
        "selected_price_range": selected_price_range,
    }
    return render(request, "shop.html", context)

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        # ✅ Handle AJAX request
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            cart_count = Cart.objects.filter(user=request.user).count()
            return JsonResponse({
                "success": True,
                "cart_count": cart_count,
                "product_name": product.name,
            })

        messages.success(request, f"{product.name} added to cart!", extra_tags="cart")
    else:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "error": "login_required"})
        messages.error(request, "Please login to add products to your cart.", extra_tags="login")

    return redirect("home")


@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)

    # Calculate subtotal
    subtotal = sum(item.total_price for item in cart_items)

    # Use Decimal for tax and shipping
    tax = subtotal * Decimal('0.05')  # 5% tax
    shipping = Decimal('20') if subtotal < Decimal('500') else Decimal('0')
    total = subtotal + tax + shipping

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "cart_count": cart_items.count(),
        "subtotal": subtotal,
        "tax": tax,
        "shipping": shipping,
        "total": total,
    })


def update_cart(request, item_id, action):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)

    if action == "increase":
        cart_item.quantity += 1
    elif action == "decrease" and cart_item.quantity > 1:
        cart_item.quantity -= 1
    cart_item.save()

    cart_items = Cart.objects.filter(user=request.user)
    subtotal = sum(item.total_price for item in cart_items)
    tax = subtotal * Decimal('0.05')
    shipping = Decimal('20') if subtotal < Decimal('500') else Decimal('0')
    total = subtotal + tax + shipping

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "item_id": cart_item.id,
            "quantity": cart_item.quantity,
            "item_total": f"{cart_item.total_price:.2f}",
            "subtotal": f"{subtotal:.2f}",
            "tax": f"{tax:.2f}",
            "shipping": f"{shipping:.2f}",
            "total": f"{total:.2f}",
            "cart_count": cart_items.count(),
        })

    return redirect("cart_view")

def remove_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.delete()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # Recalculate totals after removal
        cart_items = Cart.objects.filter(user=request.user)
        subtotal = sum(item.total_price for item in cart_items)
        tax = subtotal * Decimal("0.05")
        shipping = Decimal("20") if subtotal < Decimal("500") and subtotal > 0 else Decimal("0")
        total = subtotal + tax + shipping

        return JsonResponse({
            "success": True,
            "item_id": item_id,
            "subtotal": f"{subtotal:.2f}",
            "tax": f"{tax:.2f}",
            "shipping": f"{shipping:.2f}",
            "total": f"{total:.2f}",
            "cart_count": cart_items.count(),
        })

    return redirect("cart_view")

@login_required
def payment(request):
    order_placed = False
    payment_methods = PaymentMethod.objects.all()

    if request.method == "POST":
        form = BillingForm(request.POST)
        selected_payment_id = request.POST.get('payment')
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect('cart_view')

        if form.is_valid() and selected_payment_id:
            billing = form.save(commit=False)
            billing.user = request.user
            billing.save()

            payment_method = get_object_or_404(PaymentMethod, id=selected_payment_id)

            subtotal = sum(Decimal(item.total_price) for item in cart_items)
            tax = subtotal * Decimal('0.05')
            shipping = Decimal('20') if subtotal < Decimal('500') else Decimal('0')
            total = subtotal + tax + shipping

            order = Order.objects.create(
                user=request.user,
                billing=billing,
                payment_method=payment_method,
                total=total
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )

            cart_items.delete()
            request.session['order_placed'] = True
            return redirect('payment')

    else:
        form = BillingForm()

    cart_items = Cart.objects.filter(user=request.user)
    if request.session.get('order_placed'):
        order_placed = True
        del request.session['order_placed']

    if not cart_items.exists() and not order_placed:
        return redirect('cart_view')

    if cart_items.exists():
        subtotal = sum(Decimal(item.total_price) for item in cart_items)
        tax = subtotal * Decimal('0.05')
        shipping = Decimal('20') if subtotal < Decimal('500') else Decimal('0')
        total = subtotal + tax + shipping
    else:
        subtotal = tax = shipping = total = Decimal('0')

    return render(request, 'payment.html', {
        'form': form,
        'payment_methods': payment_methods,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'total': total,
        'order_placed': order_placed,
    })

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "my_orders.html", {"orders": orders})

from django.shortcuts import render, get_object_or_404
from .models import Order

def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Define steps
    steps = ["Order Confirmed", "Shipped", "Out for Delivery", "Delivered"]

    # Map status to step index
    status_map = {
        "Confirmed": 0,
        "Shipped": 1,
        "Out for Delivery": 2,
        "Delivered": 3,
    }
    current_step = status_map.get(order.status, 0)

    context = {
        "order": order,
        "steps": steps,
        "current_step": current_step,
    }
    return render(request, "track_order.html", context)


def about(request):
    school_products=SchoolProduct.objects.all()
    team_members=TeamMember.objects.all()
    sections=AboutSection.objects.prefetch_related("images").all()
    return render(request, 'about.html', {'school_products':school_products, 'sections': sections, 'team_members':team_members})


def contact(request):
    contacts = ContactInfo.objects.all()

    if request.method=="POST":
        form=ContactForm(request.POST)
        if form.is_valid():
            contact_msg=form.save()

            # Email to admin
            send_mail(
                subject=f"New message from {contact_msg.name}",
                message=f"Name: {contact_msg.name}\n"
                f"Email: {contact_msg.email}\n"
                f"Phone: {contact_msg.phone}\n\n"
                f"Message: \n{contact_msg.message}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )

            # Confirmation email to user
            send_mail(
                subject="✅ Thanks for Contacting Us",
                message=f"Hello {contact_msg.name},\n\n"
                        f"We received your message and will respond soon.\n\n",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[contact_msg.email],
                fail_silently=False,
            )

            messages.success(request, "Message Sent")
            return redirect("contact")
    else:
        form=ContactForm()

    return render(request, 'contact.html', {'contacts':contacts, 'form':form})

def register_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            messages.error(request, "Invalid password", extra_tags="register")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists", extra_tags="register")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered", extra_tags="register")
        else:
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Account created successfully! Please login.", extra_tags="register")
    return redirect("home")


def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
        else:
            messages.error(request, "Invalid username or password", extra_tags="login")
    return redirect("home")

    
def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('home')

def search(request):
    query=request.GET.get("q")

    results=Product.objects.all()

    if query:
        results=results.filter(
            Q(name__icontains=query) | Q(category__name__icontains=query)
        )

    return render(request, "search.html", {"results": results, "query": query},)

