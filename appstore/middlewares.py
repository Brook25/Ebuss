



class LogCountryMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        geo_lat = request.headers.get('Geo-lat', None)
        geo_lon = request.headers.get('Geo-lon', None)
        if (geo_lat and geo_lon):
            pass
        

    def get_geo_spatial_data(self, request):
        pass

    def get_loc_from_ip(self, request):
        pass

    def log_country_data(self):
        pass
