from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarMake, CarModel, CarDealer, DealerReview
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_request, get_dealer_reviews_from_cf, post_request, analyze_review_sentiments

from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def index_sample(request):
    context={}
    return render(request, 'djangoapp/index_sample.html', context)

# Create an `about` view to render a static about page
# def about(request):
# ...
def about(request):
    context={}
    return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
#def contact(request):
def contact(request):
    context={}
    return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
# def login_request(request):
# ...
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
# ...
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        #url = "your-cloud-function-domain/dealerships/dealer-get"
        url = "https://d723dfa3.us-south.apigw.appdomain.cloud/dealership-capstone-api/dealerships/dealer-get"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context["dealerships"] = dealerships
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        #url = "your-cloud-function-domain/dealerships/dealer-get"
        url = "https://d723dfa3.us-south.apigw.appdomain.cloud/dealership-capstone-api/review"
        url_dealers = "https://d723dfa3.us-south.apigw.appdomain.cloud/dealership-capstone-api/dealerships/dealer-get"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url,dealer_id)
        #context["dealer_id"] = dealer_id
        # Concat all dealer's short name
        reviews_text = ', '.join([review.review for review in reviews])
        
        #add language analyzer result for display
        print("ANALYZE")
        #sentiment = {}
        #for review in reviews:
        #    if review.sentiment:
        #        print(review.sentiment)
        #        if review.sentiment=="negative":
        #            sentiment["sentiment"] = "negative"
        #        elif review.sentiment=="positive":
        #            sentiment["sentiment"] = "positive"
        #        elif review.sentiment=="neutral":
        #            sentiment["sentiment"] = "neutral"
        

        #Get the reviews to load on dealers_details.html
        json_result = get_request(url)

        #get reviews and use for html
        reviews_render = []
        reviews = json_result['result']
        reviews = reviews["rows"]
        for review in reviews:
            review = review["doc"]
            if review["dealership"]==dealer_id:
                review['sentiment'] = analyze_review_sentiments(review['review'])
                reviews_render.append(review)
                #analyze review to assign the sentiment
                #print(review['sentiment'])
        #review = reviews[dealer_id-1]
        #review = review["doc"]
        #print(review["name"])

        # get the dealerships to load
        json_result = get_request(url_dealers)
            
        dealers = json_result['result']
        dealer = dealers[dealer_id-1]
        dealer = dealer["doc"]
        #dealership_no = review["dealership"]
        #print(dealer["full_name"])

        context = {
                'reviews': reviews_render,
                'reviews_count': len(reviews_render),
                'dealer_id': dealer_id,
                'dealership':dealer["full_name"],
        }
        # Return a list of dealer short name
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    url = "https://d723dfa3.us-south.apigw.appdomain.cloud/dealership-capstone-api/review"
    url_dealers = "https://d723dfa3.us-south.apigw.appdomain.cloud/dealership-capstone-api/dealerships/dealer-get"
    review = dict()
    context = {}
    json_payload = {}

    user = request.user
    carmodel = CarModel.objects.filter(dealer_id=dealer_id)
    #print(carmodel[0].carmake)
    #print("carmodel output: "+carmodel.name)

    #car_name = carmodel.name
    #context["car_name"] = car_name
    #context={"dealer_id": dealer_id}
    #print(context["car_name"])



    if (request.user.is_authenticated):
        
        #review["time"] = datetime.utcnow().isoformat()
        #review["name"] = request.POST["name"]
        #review["dealership"] = request.POST["dealership"]
        #review["review"] = request.POST["review"]
        #review["purchase"] = request.POST["purchase"]

        if request.method == "GET":
            review["time"] = datetime.utcnow().isoformat()
            json_result = get_request(url_dealers)
            
            dealers = json_result['result']
            dealer = dealers[dealer_id-1]
            dealer = dealer["doc"]
            print(dealer["full_name"])
            #review["name"] = request.POST["name"]
            #review["dealership"] = request.POST["dealership"]
            #review["review"] = request.POST["review"]
            #review["purchase"] = request.POST["purchase"]
            #print(dealers)
            context = {
                'cars': carmodel,
                'dealer_id': dealer_id,
                'full_name': dealer["full_name"],
            }
        
        
        if request.method == "POST":
            json_payload = {}
            context = {}
            context['dealer_id'] = dealer_id
            json_payload["review"] = request.POST['content']
            json_payload["name"] = request.POST['full_name']
            if request.POST['purchasecheck']=='on':
                json_payload["has_purchased"] = True
            #get the model, make and year
            json_payload["car"] = request.POST['car']
            d = dict(x.split(":") for x in json_payload["car"].split(","))
            json_payload['model'] = d['model']
            json_payload['carmake'] = d['carmake']
            json_payload['year'] = d['year']
            
            json_payload["purchase_date"] = request.POST['purchasedate']
            #print(json_payload)
            result = post_request(url, json_payload, dealerId=dealer_id)
            #print(result)
            return redirect("djangoapp:index")
            #return render(request, 'djangoapp/dealer_details.html', context)
        #return HttpResponse(result)
    return render(request, 'djangoapp/add_review.html', context)
