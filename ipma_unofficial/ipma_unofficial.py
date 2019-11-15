import logging

from flatten_json import flatten

from ipma.ipma import ipma_globalIds
from utils.genericSource import GenericSource


class ipma_dea(GenericSource):
    def __init__(self, enabled=True):
        super().__init__()
        self.enabled = enabled
        self.url = 'https://www.ipma.pt/resources.www/transf/dea/dea.json'

    def refresh_source(self):
        self.data = []

        if req := self.fetch_url('https://www.ipma.pt/resources.www/transf/dea/dea.json'):

            for data in req['data']:
                self.append_ipma_metadata(req, data)
                flat = flatten(data)
                self.data.append(flat)


class ipma_hourly(GenericSource):
    def __init__(self, enabled=True):
        super().__init__()
        self.enabled = enabled
        self.globalIds = ipma_globalIds()

    def refresh_source(self):
        self.data = []

        self.globalIds.refresh_source()

        fetched_globalIds = 0

        for globalId in self.globalIds:

            # {'idRegiao': 1, 'idAreaAviso': 'AVR', 'idConcelho': 5, 'globalIdLocal': 1010500,
            # 'latitude': '40.6413', 'idDistrito': 1, 'local': 'Aveiro', 'longitude': '-8.6535'}
            globalIdLocal = globalId['globalIdLocal']
            local = globalId['local']

            logging.getLogger().debug(f'Retrieving ipma_5days_local globalIdLocal {globalIdLocal} ({local})...')

            if req := self.fetch_url(f'http://api.ipma.pt/public-data/forecast/aggregate/{globalIdLocal}.json'):

                # retrieves a list of hourly predictions.
                for pred in req:
                    pred['globalIdLocal'] = globalIdLocal

                self.data += req

                fetched_globalIds += 1


class ipma_sto_hourly(GenericSource):
    def __init__(self, enabled=True):
        super().__init__()
        self.enabled = enabled

    def refresh_source(self):
        self.data = []

        if req := self.fetch_url('http://api.ipma.pt/public-data/observation/surface-stations/observations.json'):

            # source is organized by data and then by location
            for forecastDate in req.keys():
                for globalId in req[forecastDate].keys():

                    # some results are None
                    if req[forecastDate][globalId]:
                        req[forecastDate][globalId]['forecastDate'] = forecastDate
                        req[forecastDate][globalId]['globalIdLocal'] = globalId

                        self.data.append(req[forecastDate][globalId])


class ipma_sto_daily(GenericSource):
    def __init__(self, enabled=True):
        super().__init__()
        self.enabled = enabled

    def refresh_source(self):
        self.data = []

        if req := self.fetch_url('http://api.ipma.pt/public-data/observation/surface-stations/daily-observations.json'):

            # source has predictions by day and then by globalId
            for forecastDate in req.keys():
                for globalId in req[forecastDate].keys():

                    # some results are None
                    if req[forecastDate][globalId]:
                        req[forecastDate][globalId]['forecastDate'] = forecastDate
                        req[forecastDate][globalId]['globalIdLocal'] = globalId

                        self.data.append(req[forecastDate][globalId])


class ipma_stations(GenericSource):
    def __init__(self, enabled=True):
        super().__init__()
        self.enabled = enabled

    def refresh_source(self):
        self.data = []

        if req := self.fetch_url('http://api.ipma.pt/public-data/observation/surface-stations/stations.json'):

            # source retrieves a list with nested dictionaries inside

            for station in req:
                flat = flatten(station)
                self.data.append(flat)


class ipma_warnings(GenericSource):
    def __init__(self, enabled=True):
        super().__init__()
        self.enabled = enabled

    def refresh_source(self):
        self.data = []

        if req := self.fetch_url('http://api.ipma.pt/public-data/warnings/warnings_www.json'):

            for data in req['data']:
                self.append_ipma_metadata(req, data)
                self.data.append(data)


class ipma_locations(GenericSource):
    def __init__(self, enabled=True):
        super().__init__()
        self.enabled = enabled

    def refresh_source(self):
        self.data = []

        if req := self.fetch_url('http://api.ipma.pt/public-data/forecast/locations.json'):
            # this source retrieves a list flattened
            self.data = req


class ipma_districts(GenericSource):
    def __init__(self, enabled=True):
        super().__init__()
        self.enabled = enabled

    def refresh_source(self):
        self.data = []

        if req := self.fetch_url('http://api.ipma.pt/public-data/districts.json'):
            # this source retrieves a list flattened
            self.data = req


class ipma_wwis(GenericSource):
    def __init__(self, enabled=True):
        super().__init__()
        self.enabled = enabled

    def refresh_source(self):
        self.data = []

        for idDay in [0, 1, 2]:
            if req := self.fetch_url(f'http://api.ipma.pt/public-data/forecast/land/daily_aggregation/WORLD-WWIS-daily-forecast-day{idDay}.json'):
                for data in req['data']:
                    self.append_ipma_metadata(req, data)
                    self.data.append(data)

# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s %(funcName)s %(name)s [%(module)-12.12s] [%(levelname)-5.5s]  %(message)s",
#     # format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
#     handlers=[
#         logging.StreamHandler()
#     ])
#
# ipma_de = ipma_dea()
# ipma_hourl = ipma_hourly()
# ipma_sto_hourl = ipma_sto_hourly()
# ipma_sto_dail = ipma_sto_daily()
# ipma_station = ipma_stations()
# ipma_warning = ipma_warnings()
# ipma_location = ipma_locations()
# ipma_district = ipma_districts()
# ipma_wwi = ipma_wwis()
