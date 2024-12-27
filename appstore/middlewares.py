from geopy.geocoders import Nominatim
from appstore.settings import BASE_DIR
import geoip2.database
import os

class LogCountryMiddleware:

    def __init__(self, get_response):
        
        self.get_response = get_response
        db_path = os.getenv('IP_DB_PATH', BASE_DIR + '/shared/ip_database')
        self.geoip_reader = geoip2.database.Reader(db_path)
        
    def __call__(self, request):
        
        geo_lat = request.headers.get('Geo-lat', None)
        geo_lon = request.headers.get('Geo-lon', None)
        
        if (geo_lat and geo_lon):
            geolocator = Nominatim(user_agent='MyGeoCoder')
            location_name = geolocator.reverse((geo_lat, geo_lon), language='en')
        else:
            ip = self.get_client_ip(request)
            location = self.geoip_reader.country(ip)
            location_name = location.country.name
        
        response = self.get_response(request)
        
        self.log_country_data(location_name, request.user)

        return response

    def get_client_ip(self, request):
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        return ip


    def log_country_data(self, location_name):
        pass
