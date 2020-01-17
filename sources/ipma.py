import logging

from utils.genericSource import GenericSource


class ipma_globalIds(GenericSource):
    def __init__(self, name=None):
        super().__init__(name)
        self.url = 'http://api.ipma.pt/open-data/distrits-islands.json'

    def refresh_source(self):
        self.data = []

        if req := self.fetch_url(self.url):
            for data in req['data']:
                self.append_ipma_metadata(req, data)
                self.data.append(data)


class ipma_5days_local(GenericSource):
    def __init__(self, name=None):
        super().__init__(name)
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

            logging.getLogger().debug(f'Retrieving ipma_5days_local globalID {globalIdLocal} ({local})...')

            if req := self.fetch_url(f'http://api.ipma.pt/open-data/forecast/meteorology/cities/daily/{globalIdLocal}.json'):
                for data in req['data']:
                    self.append_ipma_metadata(req, data)

                    # this datasource has a variable tag, so let's patch it
                    data['classPrecInt'] = data.get('classPrecInt')

                    # also add globalIdLocal to the flattened result
                    data['globalIdLocal'] = globalIdLocal

                    self.data.append(data)

                fetched_globalIds += 1


class ipma_3days_day(GenericSource):
    def __init__(self, name=None):
        super().__init__(name)

    def refresh_source(self):
        self.data = []

        fetched_days = 0
        for idDay in [0, 1, 2]:
            if req := self.fetch_url(f"http://api.ipma.pt/open-data/forecast/meteorology/cities/daily/hp-daily-forecast-day{idDay}.json"):

                fetched_days += 1

                for data in req['data']:
                    self.append_ipma_metadata(req, data)

                    # this datasource has a variable tag, so let's patch it
                    data['classPrecInt'] = data.get('classPrecInt')

                    # also add globalIdLocal to the flattened result
                    data['idDay'] = idDay

                    self.data.append(data)

        logging.debug(f'Fetched {fetched_days} out of 3 days, totalling {len(self.data)} forecasts')


class ipma_seismicity(GenericSource):
    def __init__(self, name=None):
        super().__init__(name)

    def refresh_source(self):
        self.data = []

        fetched_idAreas = 0
        for idArea in [3, 7]:

            if req := self.fetch_url(f'http://api.ipma.pt/open-data/observation/seismic/{idArea}.json'):
                fetched_idAreas += 1

                for data in req['data']:
                    data['idArea'] = idArea
                    self.append_ipma_metadata(req, data)
                    self.data.append(data)

        logging.debug(f'Fetched {fetched_idAreas} out of 2 idArea, totalling {len(self.data)} events')


class ipma_weatherIds(GenericSource):
    def __init__(self, name=None):
        super().__init__(name)

    def refresh_source(self):
        self.data = []

        if req := self.fetch_url('http://api.ipma.pt/open-data/weather-type-classe.json'):
            for data in req['data']:
                self.append_ipma_metadata(req, data)
                self.data.append(data)


class ipma_windClasses(GenericSource):
    def __init__(self, name=None):
        super().__init__(name)

    def refresh_source(self):
        self.data = []

        if req := self.fetch_url('http://api.ipma.pt/open-data/wind-speed-daily-classe.json'):
            for data in req['data']:
                self.append_ipma_metadata(req, data)
                self.data.append(data)