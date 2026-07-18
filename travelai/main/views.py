from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import json
import logging
from .models import User

# Set up logging
logger = logging.getLogger(__name__)

# ------------------- Auth Views -------------------

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        if not email or not password:
            messages.error(request, "Email and password are required.")
            return redirect('register')
        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                full_name=full_name
            )
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return redirect('register')
    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Login successful.")
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')
    return render(request, 'login.html')

def logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

# ------------------- Static Pages -------------------

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def profile_page(request):
    return render(request, 'profile_page.html')

# ------------------- Enhanced API Helper Functions -------------------

def search_destination_booking(destination_name):
    """Search for destination using Booking.com API (RapidAPI)"""
    url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination"
    querystring = {"query": destination_name}
    headers = {
        "x-rapidapi-key": settings.RAPIDAPI_KEY,
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }
    
    try:
        logger.info(f"Searching destination: {destination_name}")
        response = requests.get(url, headers=headers, params=querystring, timeout=30)
        logger.info(f"API Response Status: {response.status_code}")
        logger.info(f"API Response Headers: {dict(response.headers)}")
        
        response.raise_for_status()
        data = response.json()
        logger.info(f"API Response Data: {json.dumps(data, indent=2)[:500]}...")
        
        if data.get('status') and data.get('data') and len(data['data']) > 0:
            return data['data'][0]
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching destination: {e}")
        return None

def search_hotels_booking(dest_id, checkin_date, checkout_date, adults=2):
    """Search for hotels using Booking.com API"""
    url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"
    querystring = {
        "dest_id": str(dest_id),
        "search_type": "district",
        "arrival_date": checkin_date,
        "departure_date": checkout_date,
        "adults": str(adults),
        "children_age": "0,17",
        "room_qty": "1",
        "page_number": "1",
        "languagecode": "en-us",
        "currency_code": "USD"
    }
    headers = {
        "x-rapidapi-key": settings.RAPIDAPI_KEY,
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }
    
    try:
        logger.info(f"Searching hotels for dest_id: {dest_id}")
        response = requests.get(url, headers=headers, params=querystring, timeout=30)
        logger.info(f"Hotels API Response Status: {response.status_code}")
        
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') and data.get('data') and data['data'].get('hotels'):
            return data['data']['hotels']
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching hotels: {e}")
        return []

def search_hotels_amadeus(city_code, checkin_date, checkout_date, adults=2):
    """Alternative: Amadeus Hotel API"""
    if not hasattr(settings, 'AMADEUS_API_KEY') or not settings.AMADEUS_API_KEY:
        return []
    
    # First get access token
    token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': settings.AMADEUS_CLIENT_ID,
        'client_secret': settings.AMADEUS_CLIENT_SECRET
    }
    
    try:
        token_response = requests.post(token_url, data=token_data, timeout=30)
        token_response.raise_for_status()
        access_token = token_response.json()['access_token']
        
        # Search hotels
        hotels_url = "https://test.api.amadeus.com/v3/shopping/hotel-offers"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        params = {
            'cityCode': city_code,
            'checkInDate': checkin_date,
            'checkOutDate': checkout_date,
            'adults': adults,
            'currency': 'USD'
        }
        
        response = requests.get(hotels_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return data.get('data', [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Amadeus API error: {e}")
        return []

def get_mock_hotels_data(destination, checkin_date, checkout_date, adults=2):
    """Fallback: Mock hotel data for development/testing"""
    return [
        {
            'hotel_id': '1',
            'property': {
                'name': f'Grand Hotel {destination}',
                'photoUrls': ['https://via.placeholder.com/300x200?text=Hotel+1'],
                'reviewScore': 8.5,
                'reviewScoreWord': 'Excellent'
            },
            'accessibilityLabel': f'Grand Hotel in {destination}',
            'price_breakdown': {
                'all_inclusive_price': 150,
                'currency': 'USD'
            },
            'review_score': 8.5
        },
        {
            'hotel_id': '2',
            'property': {
                'name': f'Luxury Resort {destination}',
                'photoUrls': ['https://via.placeholder.com/300x200?text=Hotel+2'],
                'reviewScore': 9.2,
                'reviewScoreWord': 'Superb'
            },
            'accessibilityLabel': f'Luxury Resort in {destination}',
            'price_breakdown': {
                'all_inclusive_price': 350,
                'currency': 'USD'
            },
            'review_score': 9.2
        },
        {
            'hotel_id': '3',
            'property': {
                'name': f'Budget Inn {destination}',
                'photoUrls': ['https://via.placeholder.com/300x200?text=Hotel+3'],
                'reviewScore': 7.8,
                'reviewScoreWord': 'Good'
            },
            'accessibilityLabel': f'Budget Inn in {destination}',
            'price_breakdown': {
                'all_inclusive_price': 85,
                'currency': 'USD'
            },
            'review_score': 7.8
        }
    ]

def search_hotels_with_fallback(destination, checkin_date, checkout_date, adults=2):
    """Search hotels with multiple providers and fallback"""
    hotels_data = []
    
    # Try Booking.com API first
    try:
        destination_info = search_destination_booking(destination)
        if destination_info and destination_info.get('dest_id'):
            hotels_data = search_hotels_booking(
                dest_id=destination_info['dest_id'],
                checkin_date=checkin_date,
                checkout_date=checkout_date,
                adults=adults
            )
            if hotels_data:
                logger.info(f"Successfully fetched {len(hotels_data)} hotels from Booking.com")
                return hotels_data, "booking"
    except Exception as e:
        logger.error(f"Booking.com API failed: {e}")
    
    # Try Amadeus API as fallback
    try:
        # You'll need city codes mapping or geocoding service
        city_code = get_city_code(destination)  # You need to implement this
        if city_code:
            hotels_data = search_hotels_amadeus(
                city_code=city_code,
                checkin_date=checkin_date,
                checkout_date=checkout_date,
                adults=adults
            )
            if hotels_data:
                logger.info(f"Successfully fetched {len(hotels_data)} hotels from Amadeus")
                return hotels_data, "amadeus"
    except Exception as e:
        logger.error(f"Amadeus API failed: {e}")
    
    # Use mock data as final fallback
    logger.warning("Using mock hotel data as fallback")
    hotels_data = get_mock_hotels_data(destination, checkin_date, checkout_date, adults)
    return hotels_data, "mock"

def get_city_code(destination):
    """Convert destination name to city code for Amadeus API"""
    # This is a simplified mapping - in production, use a geocoding service
    city_codes = {
        'paris': 'PAR',
        'london': 'LON',
        'new york': 'NYC',
        'tokyo': 'TYO',
        'madrid': 'MAD',
        'barcelona': 'BCN',
        'rome': 'ROM',
        'dubai': 'DXB'
    }
    return city_codes.get(destination.lower())

def test_api_connection():
    """Test API connection and return status"""
    results = {}
    
    # Test Booking.com API
    try:
        response = requests.get(
            "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination",
            headers={
                "x-rapidapi-key": settings.RAPIDAPI_KEY,
                "x-rapidapi-host": "booking-com15.p.rapidapi.com"
            },
            params={"query": "paris"},
            timeout=10
        )
        results['booking'] = {
            'status': response.status_code,
            'working': response.status_code == 200,
            'error': None if response.status_code == 200 else response.text
        }
    except Exception as e:
        results['booking'] = {
            'status': 'error',
            'working': False,
            'error': str(e)
        }
    
    return results

# ------------------- Updated Trip Planner Flow -------------------

def trip_planner(request):
    if request.method == "POST":
        trip_data = {
            "destination": request.POST.get("destination"),
            "travelers": request.POST.get("travelers", 2),
            "start_date": request.POST.get("startDate"),
            "end_date": request.POST.get("endDate"),
            "budget": request.POST.get("budget", 0),
            "preferences": request.POST.getlist("preferences"),
        }
        request.session['trip_data'] = trip_data
        return redirect('hotels')
    return render(request, 'trip_planner.html')

def hotels(request):
    trip_data = request.session.get('trip_data')
    if not trip_data:
        messages.error(request, "No trip data found. Please plan your trip first.")
        return redirect('trip_planner')

    hotels_data = []
    error_message = None
    api_source = None

    try:
        # Use the improved search function with fallback
        hotels_data, api_source = search_hotels_with_fallback(
            destination=trip_data['destination'],
            checkin_date=trip_data['start_date'],
            checkout_date=trip_data['end_date'],
            adults=int(trip_data.get('travelers', 2))
        )
        
        if not hotels_data:
            error_message = f"No hotels found for {trip_data['destination']}. Please try a different destination."
        
    except Exception as e:
        logger.error(f"Error in hotels view: {e}")
        error_message = "There was an error fetching hotel data. Please try again."
        # Use mock data as final fallback
        hotels_data = get_mock_hotels_data(trip_data['destination'], trip_data['start_date'], trip_data['end_date'])
        api_source = "mock"

    if request.method == "POST" and 'hotel' in request.POST:
        request.session['hotel'] = request.POST.get('hotel')
        return redirect('places')

    context = {
        "trip_data": trip_data,
        "hotels_data": json.dumps(hotels_data),
        "error_message": error_message,
        "api_source": api_source,
        "total_hotels": len(hotels_data)
    }

    return render(request, 'hotels.html', context)

def places(request):
    trip_data = request.session.get('trip_data')
    if not trip_data:
        messages.error(request, "No trip data found. Please plan your trip first.")
        return redirect('trip_planner')
    if request.method == "POST":
        request.session['places'] = request.POST.getlist('places')
        return redirect('expenses')
    return render(request, 'places.html', {"trip_data": trip_data})

def expenses(request):
    trip_data = request.session.get('trip_data')
    hotel = request.session.get('hotel')
    places = request.session.get('places')
    if not trip_data or not hotel or not places:
        messages.error(request, "Missing trip data. Please plan your trip first.")
        return redirect('trip_planner')
    return render(request, 'expenses.html', {
        "trip_data": trip_data,
        "hotel": hotel,
        "places": places,
    })

# ------------------- AJAX Endpoints -------------------

@require_http_methods(["GET"])
def filter_hotels(request):
    """AJAX endpoint to filter hotels based on criteria"""
    trip_data = request.session.get('trip_data')
    if not trip_data:
        return JsonResponse({'error': 'No trip data found'}, status=400)

    price_filter = request.GET.get('price_filter')
    rating_filter = request.GET.get('rating_filter')
    sort_filter = request.GET.get('sort_filter')

    try:
        # Get hotels data with fallback
        hotels_data, api_source = search_hotels_with_fallback(
            destination=trip_data['destination'],
            checkin_date=trip_data['start_date'],
            checkout_date=trip_data['end_date'],
            adults=int(trip_data.get('travelers', 2))
        )

        # Apply filters
        filtered_hotels = apply_hotel_filters(hotels_data, price_filter, rating_filter, sort_filter)

        return JsonResponse({
            'hotels': filtered_hotels,
            'api_source': api_source,
            'total': len(filtered_hotels)
        })
    except Exception as e:
        logger.error(f"Error in filter_hotels: {e}")
        return JsonResponse({'error': 'Failed to filter hotels'}, status=500)

@require_http_methods(["GET"])
def api_status(request):
    """AJAX endpoint to check API status"""
    status = test_api_connection()
    return JsonResponse(status)

def apply_hotel_filters(hotels_data, price_filter=None, rating_filter=None, sort_filter=None):
    """Apply filters to hotel data"""
    filtered = hotels_data.copy()

    if price_filter:
        if price_filter == 'budget':
            filtered = [h for h in filtered if h.get('price_breakdown', {}).get('all_inclusive_price', 999) < 100]
        elif price_filter == 'mid':
            filtered = [h for h in filtered if 100 <= h.get('price_breakdown', {}).get('all_inclusive_price', 0) <= 250]
        elif price_filter == 'luxury':
            filtered = [h for h in filtered if h.get('price_breakdown', {}).get('all_inclusive_price', 0) > 250]

    if rating_filter:
        min_rating = float(rating_filter)
        filtered = [h for h in filtered if h.get('review_score', 0) >= min_rating]

    if sort_filter:
        if sort_filter == 'price_low':
            filtered.sort(key=lambda h: h.get('price_breakdown', {}).get('all_inclusive_price', 9999))
        elif sort_filter == 'price_high':
            filtered.sort(key=lambda h: h.get('price_breakdown', {}).get('all_inclusive_price', 0), reverse=True)
        elif sort_filter == 'rating':
            filtered.sort(key=lambda h: h.get('review_score', 0), reverse=True)

    return filtered
def normalize_hotel_data(hotels_data, api_source):
    """Normalize hotel data from different APIs to a consistent format"""
    normalized_hotels = []
    
    for hotel in hotels_data:
        try:
            if api_source == "booking":
                # Booking.com API structure
                normalized_hotel = {
                    'hotel_id': str(hotel.get('hotel_id', '')),
                    'hotel_name': hotel.get('property', {}).get('name', 'Hotel Name Not Available'),
                    'district': hotel.get('district', ''),
                    'city': hotel.get('city', ''),
                    'review_score': hotel.get('property', {}).get('reviewScore', 0),
                    'review_score_word': hotel.get('property', {}).get('reviewScoreWord', 'No Rating'),
                    'max_photo_url': hotel.get('property', {}).get('photoUrls', [None])[0],
                    'min_total_price': hotel.get('price_breakdown', {}).get('all_inclusive_price', 0),
                    'currency': hotel.get('price_breakdown', {}).get('currency', 'USD'),
                    'is_free_cancellable': hotel.get('is_free_cancellable', False),
                    'has_swimming_pool': hotel.get('has_swimming_pool', False),
                    'is_beach_front': hotel.get('is_beach_front', False),
                    'has_free_parking': hotel.get('has_free_parking', False),
                    'is_city_center': hotel.get('is_city_center', False),
                    'accessibility_label': hotel.get('accessibilityLabel', ''),
                    'price_breakdown': hotel.get('price_breakdown', {})
                }
            elif api_source == "amadeus":
                # Amadeus API structure
                offer = hotel.get('offers', [{}])[0] if hotel.get('offers') else {}
                price = offer.get('price', {})
                
                normalized_hotel = {
                    'hotel_id': str(hotel.get('hotel', {}).get('hotelId', '')),
                    'hotel_name': hotel.get('hotel', {}).get('name', 'Hotel Name Not Available'),
                    'district': hotel.get('hotel', {}).get('address', {}).get('cityName', ''),
                    'city': hotel.get('hotel', {}).get('address', {}).get('cityName', ''),
                    'review_score': 0,  # Amadeus doesn't provide ratings in this endpoint
                    'review_score_word': 'No Rating',
                    'max_photo_url': None,  # Would need additional API call
                    'min_total_price': float(price.get('total', 0)),
                    'currency': price.get('currency', 'USD'),
                    'is_free_cancellable': offer.get('policies', {}).get('cancellation', {}).get('type') == 'FULL_STAY',
                    'has_swimming_pool': False,  # Would need hotel details API
                    'is_beach_front': False,
                    'has_free_parking': False,
                    'is_city_center': False,
                    'accessibility_label': hotel.get('hotel', {}).get('name', ''),
                    'price_breakdown': {
                        'all_inclusive_price': float(price.get('total', 0)),
                        'currency': price.get('currency', 'USD')
                    }
                }
            else:
                # Mock data - already in correct format
                normalized_hotel = {
                    'hotel_id': str(hotel.get('hotel_id', '')),
                    'hotel_name': hotel.get('property', {}).get('name', 'Hotel Name Not Available'),
                    'district': 'City Center',
                    'city': hotel.get('city', ''),
                    'review_score': hotel.get('property', {}).get('reviewScore', hotel.get('review_score', 0)),
                    'review_score_word': hotel.get('property', {}).get('reviewScoreWord', 'No Rating'),
                    'max_photo_url': hotel.get('property', {}).get('photoUrls', [None])[0],
                    'min_total_price': hotel.get('price_breakdown', {}).get('all_inclusive_price', 0),
                    'currency': hotel.get('price_breakdown', {}).get('currency', 'USD'),
                    'is_free_cancellable': True,
                    'has_swimming_pool': hotel.get('hotel_id') in ['1', '2'],
                    'is_beach_front': hotel.get('hotel_id') == '2',
                    'has_free_parking': True,
                    'is_city_center': hotel.get('hotel_id') in ['1', '3'],
                    'accessibility_label': hotel.get('accessibilityLabel', ''),
                    'price_breakdown': hotel.get('price_breakdown', {})
                }
            
            normalized_hotels.append(normalized_hotel)
            
        except Exception as e:
            logger.error(f"Error normalizing hotel data: {e}")
            continue
    
    return normalized_hotels

def search_hotels_with_fallback(destination, checkin_date, checkout_date, adults=2):
    """Search hotels with multiple providers and fallback - Updated with normalization"""
    hotels_data = []
    
    # Try Booking.com API first
    try:
        destination_info = search_destination_booking(destination)
        if destination_info and destination_info.get('dest_id'):
            raw_hotels = search_hotels_booking(
                dest_id=destination_info['dest_id'],
                checkin_date=checkin_date,
                checkout_date=checkout_date,
                adults=adults
            )
            if raw_hotels:
                hotels_data = normalize_hotel_data(raw_hotels, "booking")
                logger.info(f"Successfully fetched {len(hotels_data)} hotels from Booking.com")
                return hotels_data, "booking"
    except Exception as e:
        logger.error(f"Booking.com API failed: {e}")
    
    # Try Amadeus API as fallback
    try:
        city_code = get_city_code(destination)
        if city_code:
            raw_hotels = search_hotels_amadeus(
                city_code=city_code,
                checkin_date=checkin_date,
                checkout_date=checkout_date,
                adults=adults
            )
            if raw_hotels:
                hotels_data = normalize_hotel_data(raw_hotels, "amadeus")
                logger.info(f"Successfully fetched {len(hotels_data)} hotels from Amadeus")
                return hotels_data, "amadeus"
    except Exception as e:
        logger.error(f"Amadeus API failed: {e}")
    
    # Use mock data as final fallback
    logger.warning("Using mock hotel data as fallback")
    raw_hotels = get_mock_hotels_data(destination, checkin_date, checkout_date, adults)
    hotels_data = normalize_hotel_data(raw_hotels, "mock")
    return hotels_data, "mock"

# Updated hotels view
def hotels(request):
    trip_data = request.session.get('trip_data')
    if not trip_data:
        messages.error(request, "No trip data found. Please plan your trip first.")
        return redirect('trip_planner')

    hotels_data = []
    error_message = None
    api_source = None

    try:
        # Use the improved search function with fallback
        hotels_data, api_source = search_hotels_with_fallback(
            destination=trip_data['destination'],
            checkin_date=trip_data['start_date'],
            checkout_date=trip_data['end_date'],
            adults=int(trip_data.get('travelers', 2))
        )
        
        if not hotels_data:
            error_message = f"No hotels found for {trip_data['destination']}. Please try a different destination."
        
    except Exception as e:
        logger.error(f"Error in hotels view: {e}")
        error_message = "There was an error fetching hotel data. Please try again."
        # Use mock data as final fallback
        raw_hotels = get_mock_hotels_data(trip_data['destination'], trip_data['start_date'], trip_data['end_date'])
        hotels_data = normalize_hotel_data(raw_hotels, "mock")
        api_source = "mock"

    if request.method == "POST" and 'hotel' in request.POST:
        request.session['hotel'] = request.POST.get('hotel')
        return redirect('places')

    context = {
        "trip_data": trip_data,
        "hotels_data": json.dumps(hotels_data),
        "error_message": error_message,
        "api_source": api_source,
        "total_hotels": len(hotels_data)
    }

    return render(request, 'hotels.html', context)

# Updated filter function
def apply_hotel_filters(hotels_data, price_filter=None, rating_filter=None, sort_filter=None):
    """Apply filters to hotel data - Updated for normalized structure"""
    filtered = hotels_data.copy()

    if price_filter:
        if price_filter == 'budget':
            filtered = [h for h in filtered if h.get('min_total_price', 999) < 100]
        elif price_filter == 'mid':
            filtered = [h for h in filtered if 100 <= h.get('min_total_price', 0) <= 250]
        elif price_filter == 'luxury':
            filtered = [h for h in filtered if h.get('min_total_price', 0) > 250]

    if rating_filter:
        min_rating = float(rating_filter)
        filtered = [h for h in filtered if h.get('review_score', 0) >= min_rating]

    if sort_filter:
        if sort_filter == 'price_low':
            filtered.sort(key=lambda h: h.get('min_total_price', 9999))
        elif sort_filter == 'price_high':
            filtered.sort(key=lambda h: h.get('min_total_price', 0), reverse=True)
        elif sort_filter == 'rating':
            filtered.sort(key=lambda h: h.get('review_score', 0), reverse=True)

    return filtered

@require_http_methods(["GET"])
def filter_hotels(request):
    """AJAX endpoint to filter hotels based on criteria - Updated"""
    trip_data = request.session.get('trip_data')
    if not trip_data:
        return JsonResponse({'error': 'No trip data found'}, status=400)

    price_filter = request.GET.get('price_filter')
    rating_filter = request.GET.get('rating_filter')
    sort_filter = request.GET.get('sort_filter')

    try:
        # Get hotels data with fallback
        hotels_data, api_source = search_hotels_with_fallback(
            destination=trip_data['destination'],
            checkin_date=trip_data['start_date'],
            checkout_date=trip_data['end_date'],
            adults=int(trip_data.get('travelers', 2))
        )

        # Apply filters
        filtered_hotels = apply_hotel_filters(hotels_data, price_filter, rating_filter, sort_filter)

        return JsonResponse({
            'hotels': filtered_hotels,
            'api_source': api_source,
            'total': len(filtered_hotels)
        })
    except Exception as e:
        logger.error(f"Error in filter_hotels: {e}")
        return JsonResponse({'error': 'Failed to filter hotels'}, status=500)
    
import requests
from django.conf import settings

# Add to your views.py

def get_destination_coordinates(destination_name):
    """Get coordinates for a destination using OpenCage Geocoding API"""
    if not hasattr(settings, 'OPENCAGE_API_KEY'):
        return None
    
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        'q': destination_name,
        'key': settings.OPENCAGE_API_KEY,
        'limit': 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('results'):
            geometry = data['results'][0]['geometry']
            return {
                'lat': geometry['lat'],
                'lng': geometry['lng']
            }
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
    
    return None

def search_tourist_places_opentripmap(lat, lng, radius=5000):
    """Search tourist places using OpenTripMap API"""
    if not hasattr(settings, 'OPENTRIPMAP_API_KEY'):
        return []
    
    url = "https://api.opentripmap.com/0.1/en/places/radius"
    params = {
        'radius': radius,
        'lon': lng,
        'lat': lat,
        'rate': 2,  # Minimum rating (1-3)
        'limit': 50,
        'apikey': settings.OPENTRIPMAP_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        places = response.json()
        
        # Get detailed info for each place
        detailed_places = []
        for place in places[:20]:  # Limit to 20 places
            xid = place.get('xid')
            if xid:
                details = get_place_details_opentripmap(xid)
                if details:
                    detailed_places.append(details)
        
        return detailed_places
    except Exception as e:
        logger.error(f"OpenTripMap API error: {e}")
        return []

def get_place_details_opentripmap(xid):
    """Get detailed info about a specific place"""
    if not hasattr(settings, 'OPENTRIPMAP_API_KEY'):
        return None
    
    url = f"https://api.opentripmap.com/0.1/en/places/xid/{xid}"
    params = {'apikey': settings.OPENTRIPMAP_API_KEY}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error getting place details: {e}")
        return None

def search_places_google(destination, api_key):
    """Search places using Google Places API"""
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        'query': f'tourist attractions in {destination}',
        'key': api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json().get('results', [])
    except Exception as e:
        logger.error(f"Google Places API error: {e}")
        return []

def categorize_place(kinds, name):
    """Categorize a place based on its 'kinds' tags"""
    kinds_lower = kinds.lower() if kinds else ""
    name_lower = name.lower() if name else ""
    
    if any(k in kinds_lower for k in ['museum', 'art', 'gallery']):
        return 'museums'
    elif any(k in kinds_lower for k in ['park', 'garden', 'nature']):
        return 'parks'
    elif any(k in kinds_lower for k in ['shop', 'market', 'mall']):
        return 'shopping'
    elif any(k in kinds_lower for k in ['restaurant', 'food', 'cafe']):
        return 'food'
    elif any(k in kinds_lower for k in ['theatre', 'cinema', 'entertainment']):
        return 'entertainment'
    elif any(k in kinds_lower for k in ['monument', 'architecture', 'historic', 'church', 'temple', 'tower']):
        return 'landmarks'
    else:
        return 'landmarks'

def get_place_icon(category):
    """Get emoji icon for category"""
    icons = {
        'landmarks': '🏛️',
        'museums': '🎨',
        'parks': '🌳',
        'shopping': '🛍️',
        'food': '🍽️',
        'entertainment': '🎭'
    }
    return icons.get(category, '📍')

def normalize_places_data(places_data, source='opentripmap'):
    """Normalize places data from different sources"""
    normalized = []
    
    for idx, place in enumerate(places_data):
        try:
            if source == 'opentripmap':
                category = categorize_place(place.get('kinds', ''), place.get('name', ''))
                normalized_place = {
                    'id': idx + 1,
                    'name': place.get('name', 'Unknown Place'),
                    'category': category,
                    'description': place.get('info', {}).get('descr', 'No description available.')[:150] + '...',
                    'rating': min(5.0, (place.get('rate', 1) * 1.5 + 3)),  # Convert 1-3 to ~4-5
                    'duration': '1-2 hours',
                    'price': 'Free' if 'free' in place.get('kinds', '').lower() else '$10-20',
                    'image': get_place_icon(category),
                    'distance': f"{place.get('dist', 0):.1f} km" if place.get('dist') else 'N/A',
                    'address': place.get('address', {}).get('road', ''),
                    'wikipedia': place.get('wikipedia', ''),
                    'kinds': place.get('kinds', '')
                }
            elif source == 'google':
                # Determine category from types
                types = place.get('types', [])
                category = 'landmarks'
                if 'museum' in types:
                    category = 'museums'
                elif 'park' in types:
                    category = 'parks'
                elif 'shopping_mall' in types:
                    category = 'shopping'
                elif 'restaurant' in types:
                    category = 'food'
                
                normalized_place = {
                    'id': idx + 1,
                    'name': place.get('name', 'Unknown Place'),
                    'category': category,
                    'description': place.get('formatted_address', 'No description available.'),
                    'rating': place.get('rating', 4.0),
                    'duration': '1-2 hours',
                    'price': '$10-20',
                    'image': get_place_icon(category),
                    'distance': 'N/A',
                    'address': place.get('formatted_address', ''),
                    'place_id': place.get('place_id', '')
                }
            else:  # mock
                normalized_place = place
            
            normalized.append(normalized_place)
        except Exception as e:
            logger.error(f"Error normalizing place: {e}")
            continue
    
    return normalized

def get_mock_places_data(destination):
    """Fallback mock data for places"""
    return [
        {
            'id': 1,
            'name': f'Historic Center of {destination}',
            'category': 'landmarks',
            'description': 'Explore the historic heart of the city with its ancient architecture and cultural landmarks.',
            'rating': 4.6,
            'duration': '2-3 hours',
            'price': 'Free',
            'image': '🏛️',
            'distance': '0.5 km'
        },
        {
            'id': 2,
            'name': f'{destination} City Museum',
            'category': 'museums',
            'description': 'Discover the rich history and culture through fascinating exhibits and collections.',
            'rating': 4.4,
            'duration': '2-3 hours',
            'price': '$15',
            'image': '🎨',
            'distance': '1.2 km'
        },
        {
            'id': 3,
            'name': f'Central Park {destination}',
            'category': 'parks',
            'description': 'A beautiful green space perfect for relaxation, picnics, and outdoor activities.',
            'rating': 4.5,
            'duration': '1-2 hours',
            'price': 'Free',
            'image': '🌳',
            'distance': '1.8 km'
        },
        {
            'id': 4,
            'name': f'{destination} Shopping District',
            'category': 'shopping',
            'description': 'Browse local boutiques, international brands, and unique souvenir shops.',
            'rating': 4.3,
            'duration': '2-4 hours',
            'price': 'Varies',
            'image': '🛍️',
            'distance': '1.0 km'
        },
        {
            'id': 5,
            'name': f'Local Food Market',
            'category': 'food',
            'description': 'Experience authentic local cuisine and fresh produce at this bustling market.',
            'rating': 4.7,
            'duration': '1-2 hours',
            'price': '$20-40',
            'image': '🍽️',
            'distance': '2.3 km'
        },
        {
            'id': 6,
            'name': f'{destination} Theater District',
            'category': 'entertainment',
            'description': 'Enjoy world-class performances, shows, and cultural entertainment.',
            'rating': 4.5,
            'duration': '2-3 hours',
            'price': '$30-100',
            'image': '🎭',
            'distance': '1.5 km'
        }
    ]

def search_places_with_fallback(destination):
    """Search for tourist places with multiple API fallbacks"""
    places_data = []
    api_source = None
    
    # Try OpenTripMap API first (requires coordinates)
    try:
        coords = get_destination_coordinates(destination)
        if coords:
            places_data = search_tourist_places_opentripmap(coords['lat'], coords['lng'])
            if places_data:
                places_data = normalize_places_data(places_data, 'opentripmap')
                logger.info(f"Fetched {len(places_data)} places from OpenTripMap")
                return places_data, 'opentripmap'
    except Exception as e:
        logger.error(f"OpenTripMap failed: {e}")
    
    # Try Google Places API as fallback
    try:
        if hasattr(settings, 'GOOGLE_PLACES_API_KEY'):
            places_data = search_places_google(destination, settings.GOOGLE_PLACES_API_KEY)
            if places_data:
                places_data = normalize_places_data(places_data, 'google')
                logger.info(f"Fetched {len(places_data)} places from Google Places")
                return places_data, 'google'
    except Exception as e:
        logger.error(f"Google Places failed: {e}")
    
    # Use mock data as final fallback
    logger.warning(f"Using mock places data for {destination}")
    places_data = get_mock_places_data(destination)
    return places_data, 'mock'

# Updated places view
def places(request):
    trip_data = request.session.get('trip_data')
    if not trip_data:
        messages.error(request, "No trip data found. Please plan your trip first.")
        return redirect('trip_planner')
    
    destination = trip_data.get('destination', '')
    places_data = []
    api_source = None
    
    try:
        places_data, api_source = search_places_with_fallback(destination)
    except Exception as e:
        logger.error(f"Error fetching places: {e}")
        places_data = get_mock_places_data(destination)
        api_source = 'mock'
    
    if request.method == "POST":
        request.session['places'] = request.POST.getlist('places')
        return redirect('expenses')
    
    context = {
        'trip_data': trip_data,
        'destination': destination,
        'checkin_date': trip_data.get('start_date', ''),
        'checkout_date': trip_data.get('end_date', ''),
        'places_data': json.dumps(places_data),
        'api_source': api_source,
        'total_places': len(places_data)
    }
    
    return render(request, 'places.html', context)