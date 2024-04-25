from django.db.models import Q
from platforms.models import Platform, Inquiry, Bid
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from platforms.forms import SearchForm, InquiryForm, BidForm
from platforms.notifications import send_inquiry_notification
from django.contrib import messages
from platforms import forms


# Create your views here.

@login_required(login_url='login')
def home(request):
    platform = Platform.objects.all()
    print('>>>>>>>>>>>>',Bid.objects.filter(property = platform[0]))
    for i in platform:
        # Get the highest bid for the platform
        highest_bid = Bid.objects.filter(property = i)
        print(highest_bid)
    return render(request, 'home.html', {
        "platform": platform, 'platform_bids': None,
    })


def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if not (username and email and password1 and password2):
            # return HttpResponse("Please fill in all the fields")
            return redirect("signup")
        if password1 != password2:
            # return HttpResponse("Password didn't matched!")
            return redirect("signup")

        else:
            my_user = User.objects.create_user(username, email, password1)
            my_user.save()
            return redirect("home")

    return render(request, 'signup.html')


def loginPage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('pass')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return redirect('login')
    return render(request, 'login.html')


def logoutPage(request):
    logout(request)
    return redirect('login')


def search(request):
    form = SearchForm(request.GET or None)
    results = None

    if form.is_valid():
        query = form.cleaned_data['query']

        results = Platform.objects.filter(
            Q(title__icontains=query) |
            Q(property_type__icontains=query) |
            Q(city__icontains=query) |
            Q(country__icontains=query) |
            Q(location__icontains=query)
            # Add other fields you want to search in as necessary
        )

    return render(request, 'search.html', {
        'form': form,
        'results': results,
    })


def filters(request):
    # Initialize form to filter all Platform objects initially
    form = Platform.objects.all()

    # Get query parameters from request
    title = request.GET.get('title')
    location = request.GET.get('location')
    city = request.GET.get('city')
    view_count_min = request.GET.get('view_count_min')
    view_count_max = request.GET.get('view_count_max')
    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    category = request.GET.get('category')

    # Apply filters based on request parameters
    if title:
        form = form.filter(title__icontains=title)
    if location:
        form = form.filter(location__icontains=location)
    if city:
        form = form.filter(city__icontains=city)
    if view_count_min:
        form = form.filter(view_count__gte=view_count_min)
    if view_count_max:
        form = form.filter(view_count__lte=view_count_max)
    if date_min:
        form = form.filter(publish_date__gte=date_min)
    if date_max:
        form = form.filter(publish_date__lte=date_max)
    if category and category != 'Choose...':
        form = form.filter(property_type=category)

    # Query distinct property types from Platform
    unique_property_types = Platform.objects.values_list('property_type', flat=True).distinct()

    # Pass form and unique_categories to the template
    return render(request, 'filters.html', {
        'form': form,
        'unique_property_types': unique_property_types
    })


# def details(request, p_id):
# platform =
# return render(request, 'details.html', {
#     "platform": platform
#  })

def details(request, property_id):
    platform = get_object_or_404(Platform, pk=property_id)
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.property = platform
            inquiry.user = request.user if request.user.is_authenticated else None
            inquiry.save()
            send_inquiry_notification(inquiry)
            return HttpResponseRedirect(reverse('details', args=[platform.id]))
    else:
        form = InquiryForm()
    return render(request, 'details.html', {'platform': platform, 'form': form})


@login_required
def inquiries(request):
    owner_properties = request.user.platform_set.all()
    inquiry = Inquiry.objects.filter(platform__in=owner_properties)
    return render(request, 'inquiries.html', {'inquiry': inquiry})


def place_bid(request, platform_id):
    platform = get_object_or_404(Platform, id=platform_id)
    if request.method == 'GET':
        form = BidForm(request.GET)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.user = request.user
            bid.property = platform
            bid.save()
            messages.success(request, f'Bid of ${bid.amount} placed successfully!')
            return redirect('home')  # Redirect to the home page or other view as needed
        else:
            messages.error(request, 'There was an issue with your bid.')
    else:
        form = BidForm()

    return render(request, 'forms.html', {'form': form, 'platform': platform})
