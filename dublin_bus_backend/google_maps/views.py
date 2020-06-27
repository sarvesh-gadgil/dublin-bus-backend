from django.http import JsonResponse
from rest_framework.views import APIView
import requests
import math
from bus_stops.models import BusStops

GOOGLE_MAPS_KEY = "AIzaSyCv4Jkj6OMUVN0swxdIzZMOYu1vaddkooY"


class GoogleMapsAutocomplete(APIView):

    def get(self, request):

        searched_bus_stops = BusStops.objects.filter(stop_name__icontains=request.query_params.get('query'))

        # Get response from Google
        response = requests.get(url="https://maps.googleapis.com/maps/api/place/autocomplete/json",
                                params={'input': request.query_params.get('query'),
                                        'key': GOOGLE_MAPS_KEY,
                                        'location': '53.357841,-6.251557', 'radius': 2000}).json()
        # Create JSON response
        payload = []

        for searched_bus_stop in searched_bus_stops:
            content = {'title': searched_bus_stop.stop_name + " (" + str(searched_bus_stop.stop_id) + ")",
                       'id': searched_bus_stop.stop_id, 'fromDB': True, 'stop_lat': searched_bus_stop.stop_lat,
                       'stop_lng': searched_bus_stop.stop_lng}
            payload.append(content)

        for result in response['predictions']:
            content = {'title': result['description'], 'id': result['place_id'], 'fromDB': False}
            payload.append(content)

        return JsonResponse(payload, safe=False)


class GoogleMapsGetPlaceByID(APIView):

    def get(self, request):
        # Get response from Google
        response = requests.get(url="https://maps.googleapis.com/maps/api/place/details/json",
                                params={'placeid': request.query_params.get('place_id'), 'key': GOOGLE_MAPS_KEY}).json()
        # Create JSON response
        content = {'lat': response['result']['geometry']['location']['lat'],
                   'lng': response['result']['geometry']['location']['lng']}

        all_bus_stops = BusStops.objects.all()

        # Create JSON response
        payload = []
        for bus_stop in all_bus_stops:
            if self.calculate_distance(float(content['lat']), float(content['lng']), float(bus_stop.stop_lat),
                                       float(bus_stop.stop_lng)) <= 0.5:
                stop_details = {'stop_id': bus_stop.stop_id, 'stop_name': bus_stop.stop_name,
                                'stop_lat': bus_stop.stop_lat,
                                'stop_lng': bus_stop.stop_lng}
                payload.append(stop_details)

        return JsonResponse(payload, safe=False)

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        radlat1 = math.pi * lat1 / 180
        radlat2 = math.pi * lat2 / 180
        theta = lon1 - lon2
        radtheta = math.pi * theta / 180
        dist = math.sin(radlat1) * math.sin(radlat2) + math.cos(radlat1) * math.cos(radlat2) * math.cos(radtheta)
        if dist > 1:
            dist = 1
        dist = math.acos(dist)
        dist = dist * 180 / math.pi
        dist = dist * 60 * 1.1515
        dist = dist * 1.609344
        return dist
