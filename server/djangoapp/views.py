# This module contains views for adding reviews and getting dealer details in a Django application.
from datetime import datetime
import logging
import requests
import time

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
# from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import CarDealer, Car, DealerReview  # Import the updated CarDealer, Car, and DealerReview model
from .forms import ReviewForm

# Logger setup
logger = logging.getLogger(__name__)

def about(request):
    """
    Renders the about page.
    """
    return render(request, 'djangoapp/about.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
            # return redirect('index')
        else:
            return render(request, 'djangoapp/login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'djangoapp/login.html')

@login_required
@require_http_methods(["GET", "POST"])
# @require_http_methods(["GET"])
# favorite_car= 'my favorite car is "bmw"'

@login_required
@require_http_methods(["GET", "POST"])
def add_review(request, dealer_id):
    """Add a review for a car dealer."""
    print(f"dealer_id: {dealer_id}")  # Print the value of dealer_id
    if request.method == 'GET':
        cars = Car.objects.filter(dealer_id=dealer_id)
        form = ReviewForm()  
        print(f"cars: {cars}")  # Print the query results
        return render(request, 'djangoapp/add_review.html', {'cars': cars, 'dealer_id': dealer_id, 'form': form})
    
    elif request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.dealer_id = dealer_id
            review.save()
            return redirect('dealer_reviews', dealer_id=dealer_id)  # Updated line
        else:
            print("Form is not valid")  # Print statement for debugging
            return render(request, 'djangoapp/add_review.html', {'form': form, 'dealer_id': dealer_id})

    else:
        return HttpResponseBadRequest('Invalid HTTP method')
        
# def add_review(request, dealer_id):
#     """Add a review for a car dealer."""
#     print(f"dealer_id: {dealer_id}")  # Print the value of dealer_id
#     if request.method == 'GET':
#         cars = Car.objects.filter(dealer_id=dealer_id)
#         form = ReviewForm()  
#         print(f"cars: {cars}")  # Print the query results
#         return render(request, 'djangoapp/add_review.html', {'cars': cars, 'dealer_id': dealer_id, 'form': form})
    
#     elif request.method == 'POST':
#         form = ReviewForm(request.POST)
#         if form.is_valid():
#             review = form.save(commit=False)
#             review.dealer_id = dealer_id
#             review.save()
#             return redirect('reviews', dealer_id=dealer_id)
#         else:
#             print("Form is not valid")  # Print statement for debugging
#             return render(request, 'djangoapp/add_review.html', {'form': form, 'dealer_id': dealer_id})

#     else:
#         return HttpResponseBadRequest('Invalid HTTP method')

# def add_review(request, dealer_id):
#     """Add a review for a car dealer."""
#     print(f"dealer_id: {dealer_id}")  # Print the value of dealer_id
#     if request.method == 'GET':
#         cars = Car.objects.filter(dealer_id=dealer_id)
#         # cars = Car.objects.filter(model__dealer_id=dealer_id)
#         print(f"cars: {cars}")  # Print the query results
#         return render(request, 'djangoapp/add_review.html', {'cars': cars, 'dealer_id': dealer_id})
    
#     if request.method == 'POST':
#         # Process POST request
#         return process_add_review_post(request, dealer_id)

#     return HttpResponseBadRequest('Invalid HTTP method')

@login_required
@require_http_methods(["POST"])
def process_add_review_post(request, dealer_id):
    """Process POST request for add_review."""
    purchase_check = request.POST.get('purchasecheck')
    content = request.POST.get('content')
    purchasedate = request.POST.get('purchasedate')
    car_id = request.POST.get('car')

    if not (purchase_check and content and purchasedate and car_id):
        return HttpResponseBadRequest('Invalid or missing POST data')

    try:
        purchase_date = datetime.strptime(purchasedate, '%m/%d/%Y').isoformat()
        car = Car.objects.get(id=car_id)

        review = {
            'dealership': dealer_id,
            'name': request.user.username,
            'purchase': purchase_check,
            'review': content,
            'purchase_date': purchase_date,
            'car_make': car.make.name,
            'car_model': car.name,
            'car_year': car.year.year,
        }

        json_payload = {"review": review}
        review_post_url = (
            "https://us-south.functions.appdomain.cloud/api/v1/web/"
            "54ee907b-434c-4f03-a1b3-513c235fbeb4/default/review-post"
        )

        response = requests.post(review_post_url, json=json_payload, timeout=10)
        if response.status_code == 200:
            return redirect('djangoapp:dealer_details', dealer_id=dealer_id)
        
        logger.error('Failed to post review. Status code: %s', response.status_code)
        return HttpResponse(f'Failed to post review. Status code: {response.status_code}',
                            status=response.status_code)

    except Car.DoesNotExist:
        logger.error('Invalid car ID')
        return HttpResponseBadRequest('Invalid car ID')
    except ValueError:
        logger.error('Invalid date format')
        return HttpResponseBadRequest('Invalid date format')
    except requests.exceptions.RequestException as e:
        logger.error('Error posting review: %s', str(e))
        return HttpResponse(f'Error posting review: {str(e)}', status=500)

def contact(request):
    """
    Renders the contact page.
    """
    return render(request, 'djangoapp/contact.html')

def view_dealership(request, dealer_id):
    """View a specific car dealership."""
    try:
        dealership = CarDealer.objects.get(id=dealer_id)
    except CarDealer.DoesNotExist:
        return HttpResponseBadRequest('Dealership not found')

    return render(request, 'djangoapp/view_dealership.html', {'dealership': dealership})

def get_dealerships(request):
    logger.info("get_dealerships view called")  # Log when the function is called
    context = {}
    dealerships_url = "https://kstiner101-3000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
    dealerships = get_dealers_from_cf(dealerships_url)
    if dealerships:
        logger.info(f"Dealerships fetched successfully: {dealerships}")  # Log fetched data
        
    else:
        logger.error("No dealerships fetched")
    context['dealership_list'] = dealerships
    return render(request, 'djangoapp/index.html', context)

def get_dealer_details(request, dealer_id):
    """Get details of a car dealer and their reviews."""
    if request.method == 'GET':
        if not dealer_id:
            return HttpResponseBadRequest('Missing dealer_id')
        context = {}
        context['reviews'] = get_dealer_reviews_from_cf(dealer_id)
        print(context, "KARM", dealer_id)
        for review in context['reviews']:
            review['sentiment'] = analyze_review_sentiments(review['review'])
        try:
            dealer = CarDealer.objects.get(id=dealer_id)
            context['dealer'] = dealer
            return render(request, 'djangoapp/dealer_details.html', context)
        except CarDealer.DoesNotExist:
            return HttpResponseBadRequest('Dealership not found')

def get_dealer_reviews(request, dealer_id):
    logger.info("get_dealer_reviews view called")
    context = {}
    reviews = get_dealer_reviews_from_cf(dealer_id)
    if reviews:
        logger.info(f"Reviews fetched successfully: {reviews}")
        for review in reviews:
            review['sentiment'] = analyze_review_sentiments(review['review'])
    context['reviews_list'] = reviews
    return render(request, 'djangoapp/reviews.html', context)

@login_required
def reviews(request, dealer_id):
    """Fetch and display reviews for a specific dealer."""
    reviews = DealerReview.objects.filter(dealer_id=dealer_id)
    return render(request, 'djangoapp/reviews.html', {'reviews': reviews, 'dealer_id': dealer_id})            

def get_dealer_reviews_from_cf(dealer_id):
    """Retrieves dealer reviews from a cloud function."""
    dealer_reviews_url = (
        f"https://us-south.functions.appdomain.cloud/api/v1/web/"
        f"54ee907b-434c-4f03-a1b3-513c235fbeb4/default/myAction/{dealer_id}/reviews"
    )
    headers = {'Authorization': 'Bearer KidOOw8m-hso_lc2AgTMLdxmudJdgaJAe-dewXr62x1L'}
    response = requests.get(dealer_reviews_url, headers=headers, timeout=10)
    print(response.json(), "Karm Car")
    if response.status_code == 200:
        return response.json()
    return []

def analyze_review_sentiments(review_text):
    """Analyzes the sentiment of a review text using Watson NLU."""
    sentiment_analysis_url = (
        "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/"
        "instances/ea601f46-3769-4375-85f1-9c79b2d0f580"
    )
    headers = {'Authorization': 'Bearer KidOOw8m-hso_lc2AgTMLdxmudJdgaJAe-dewXr62x1L'}
    data = {"text": review_text}
    response = requests.post(sentiment_analysis_url, headers=headers, json=data, timeout=10)
    if response.status_code == 200:
        return response.json().get('sentiment', {}).get('document', {}).get('label', 'neutral')
    return "neutral"

@login_required
def get_dealer_by_id(request, dealer_id):
    """
    Fetches details for a specific dealer by ID.
    """
    try:
        # Fetch the dealer from the database using the dealer ID
        dealer = CarDealer.objects.get(id=dealer_id)
        # Render a template with dealer details (you need to create this template)
        return render(request, 'djangoapp/dealer_by_id.html', {'dealer': dealer})
    except CarDealer.DoesNotExist:
        # If the dealer is not found, return an error message
        return HttpResponse('Dealer not found', status=404)

def get_dealers_from_cf(dealerships_url):
    try:
        response = requests.get(dealerships_url, timeout=10)
        response.raise_for_status()  # Will raise an HTTPError for bad HTTP status codes
        dealerships = response.json()
        logger.info(f"Dealerships received: {dealerships}")
        return dealerships
    except requests.exceptions.HTTPError as errh:
        logger.error(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logger.error(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        logger.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        logger.error(f"Error: {err}")
    return []

def list_dealerships(request):
    # Fetch the list of dealerships from your database or wherever you store the data
    dealerships = CarDealer.objects.all()  # Modify this based on your data retrieval logic

    # Render the template with the list of dealerships
    return render(request, 'djangoapp/list_dealerships.html', {'dealerships': dealerships})

# Other view functions...

def some_function(request):
    if request.method == 'POST':
        # some code here
        return HttpResponse('POST request received')

# More view functions...

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('djangoapp:index')  # Replace 'index' with the name of your homepage view
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# Your existing view functions

def index(request):
    return render(request, 'djangoapp/index.html')

    # Other view functions...

def cart_json(request):
    # Replace this with the actual data you want to return
    data = {
        'items': [],
        'total': 0,
    }
    return JsonResponse(data)

def get_reviews(request, dealer_id):
    logger.info("get_reviews view called")  # Log when the function is called
    context = {}
    reviews_url = f"https://kstiner101-5000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/djangoapp/dealer/{dealer_id}/reviews"
    response = requests.get(reviews_url, timeout=10)
    if response.status_code == 200:
        reviews = response.json()
        logger.info(f"Reviews fetched successfully: {reviews}")  # Log fetched data
    else:
        reviews = []
        logger.error("No reviews fetched")
    context['reviews_list'] = reviews
    return render(request, 'djangoapp/reviews.html', context)

# def get_reviews(request, dealer_id):
#     logger.info("get_reviews view called")  # Log when the function is called
#     context = {}
#     reviews_url = f"https://kstiner101-5000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/djangoapp/dealer/{dealer_id}/reviews"
#     reviews = get_reviews_from_cf(reviews_url)
#     if reviews:
#         logger.info(f"Reviews fetched successfully: {reviews}")  # Log fetched data
#     else:
#         logger.error("No reviews fetched")
#     context['reviews_list'] = reviews
#     return render(request, 'djangoapp/reviews.html', context)
