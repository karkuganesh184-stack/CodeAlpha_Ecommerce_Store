from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem


def home(request):
    products = Product.objects.all()
    return render(request, "store/home.html", {"products": products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "product_detail.html", {"product": product})


def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session["cart"] = cart
    return redirect("cart")


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session["cart"] = cart
    return redirect("cart")


def cart(request):
    cart_data = request.session.get("cart", {})
    products = Product.objects.filter(id__in=cart_data.keys())

    items = []
    total = 0

    for product in products:
        quantity = cart_data[str(product.id)]
        item_total = product.price * quantity

        items.append({
            "product": product,
            "quantity": quantity,
            "item_total": item_total
        })

        total += item_total

    return render(request, "cart.html", {
        "items": items,
        "total": total
    })


@login_required
def checkout(request):
    cart_data = request.session.get("cart", {})

    if not cart_data:
        messages.warning(request, "Your cart is empty.")
        return redirect("home")

    products = Product.objects.filter(id__in=cart_data.keys())
    total = 0

    for product in products:
        quantity = cart_data[str(product.id)]
        total += product.price * quantity

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            total=total
        )

        for product in products:
            quantity = cart_data[str(product.id)]

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

        request.session["cart"] = {}

        messages.success(
            request,
            f"Order #{order.id} placed successfully!"
        )

        return redirect("home")

    return render(request, "checkout.html", {
        "total": total
    })


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)
        return redirect("home")

    return render(request, "register.html")


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("home")

        messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


def logout_user(request):
    logout(request)
    return redirect("home")