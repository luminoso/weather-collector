# IPMA weather-collector

*'weather-collector'* is a very simple API collector from various sources and sends the results to different outputs.

This collector exercised as pull service for [IPMA](http://www.ipma.pt/) (Instituto Português do Mar e da Atmosfera) [public APIs](http://api.ipma.pt/), where each source is queried, processed, and flattened. It can be extended to other weather-sources or any other web API.

For each different API response change, the script tries to calculate the incremental differences and sends only incremental changes since the first run. 

Main structure guideline:

-   Config file (sources and output initialization, pull time, etc)
-   Each source is a class that defines what web API to call and how to process it
-   Output definition: where to push the changes (e.g.: file system, kafka server, console, etc)
-   `weather-collector.py`: main loop

  
Basic architecture:
<p align="center"><img src="https://github.com/luminoso/weather-aggregator/raw/master/doc/main%20loop.jpg" height="500"/></p>

## 1. New source example

 1. Let's assume we want to collect IPMA available weather locations available at `http://api.ipma.pt/open-data/distrits-islands.json`

2. Create a code snippet that extends `GenericSource` and implement the API peculiarities if any.
```python
class ipma_globalIds(GenericSource):
    def __init__(self, enabled=True):
        super().__init__()
        self.url = 'http://api.ipma.pt/open-data/distrits-islands.json'

    def refresh_source(self):
        # clear latest result
        self.data = []

        if req := self.fetch_url(self.url):
            
            # globalIds API returns data within 'data' payload
            for data in req['data']:
                # flatten the metadata to the inner payload
                self.append_ipma_metadata(req, data)
                self.data.append(data)
```


3. Add new source configuration to `config.yaml`

```yaml
sources:
  ipma:
    ipma_globalIds:
```

4. Define an effortless output, for example, write to a file:

```python
def write_to_file(source: GenericSource):

    filename = f'{source.name}.txt'

    logging.debug(f'Writing {len(source)} messages to file {filename}')

    for msg in source:
        with open(filename, "a") as myfile:
            myfile.write(str(msg))

        with open(filename, "a") as myfile:
            myfile.write('\n')
```


5. Build and run Dockerfile

```bash
$ docker build -t foo . && docker run -it foo
```


## 2. I just want to see it working

By default, the service pulls everything and writes to files

1.  Build and the docker file
```bash
$ docker build -t foo . && docker run -it foo
```


## 3. Included IPMA data sources

This repo includes two types of (weather) API sources.

### Official
Official sources are APIs available at the IPMA API webpage. It is expected that they're somewhat reliable and its structure not to change.

|        id        |                     Description                     |
|:----------------:|:---------------------------------------------------:|
| ipma_globalIds   | Lookup table containing available weather locations |
| ipma_5days_local | 5 day forecast for each globalId                    |
| ipma_3days_day   | 3 day forecast for each globalId                    |
| ipma_seismicity  | Detected seismicity                                 |
| ipma_weatherIds  | Lookup table for weather forecast classes           |
| ipma_windClasses | Lookup table for weather wind classes               |


### Unofficial
Unofficial sources are sources found when parsing IPMA website. They may change anytime, and it isn't expected any reliability.

|        id       |                       Description                       |
|:---------------:|:-------------------------------------------------------:|
| ipma_dea        | Descargas elétricas atmosféricas [DEA's]                |
| ipma_hourly     | Hourly predictions for available globalIds              |
| ipma_sto_hourly | Hourly report of last 24 hours for each weather station |
| ipma_sto_daily  | Daily report of last 24 hours for each weather station  |
| ipma_stations   | Available weather stations list                         |
| ipma_warnings   | Weather warnings                                        |
| ipma_locations  | Locations list                                          |
| ipma_districts  | Districts list                                          |
| ipma_wwis       | World Weather Information Service (WWIS) report       


# 4. License

MIT
