from app import app

from urllib.parse import urlencode
from datetime import datetime, timedelta
import json

from constants import DEFAULT_DATE_FORMAT

def test_index_route():
    response = app.test_client().get('/')

    assert response.status_code == 200
    assert response.data.decode('utf-8') == 'Hello World!'

# Test for searching rates given a port and a region (default test as per example)
def test_get_rates_by_origin_port_destination_region():
    url_params = { 'date_from': '2016-01-01', 'date_to': '2016-01-10', 'origin': 'CNSGH', 'destination': 'north_europe_main' }

    response = app.test_client().get(f'/rates?{urlencode(url_params)}')

    assert response.status_code == 200

    json_body = json.loads(response.data.decode('utf-8'))

    assert_scoped_dates(json_body, url_params['date_from'], url_params['date_to'])

    date_map = { entry['day']: entry['average_price'] for entry in json_body }

    # Assertions based on example
    assert date_map['2016-01-01'] == 1112
    assert date_map['2016-01-02'] == 1112
    assert date_map['2016-01-03'] is None

# Test for searching rates given two ports
def test_get_rates_by_ports():
    url_params = { 'date_from': '2016-01-01', 'date_to': '2016-01-10', 'origin': 'CNSGH', 'destination': 'BEANR' }

    response = app.test_client().get(f'/rates?{urlencode(url_params)}')

    assert response.status_code == 200

    json_body = json.loads(response.data.decode('utf-8'))

    assert_scoped_dates(json_body, url_params['date_from'], url_params['date_to'])

    # TODO: Do custom assertion (query from DB and compare)?

# Test for searching rates given two regions
def test_get_rates_by_regions():
    url_params = { 'date_from': '2016-01-01', 'date_to': '2016-01-10', 'origin': 'china_main', 'destination': 'north_europe_main' }

    response = app.test_client().get(f'/rates?{urlencode(url_params)}')

    assert response.status_code == 200

    json_body = json.loads(response.data.decode('utf-8'))

    assert_scoped_dates(json_body, url_params['date_from'], url_params['date_to'])

    # TODO: Do custom assertion (query from DB and compare)?

# Test for missing origin and destination (400)
def test_get_rates_no_origin_destination():
    url_params = { 'date_from': '2016-01-01', 'date_to': '2016-01-10' }

    response = app.test_client().get(f'/rates?{urlencode(url_params)}')

    assert response.status_code == 400

    json_body = json.loads(response.data.decode('utf-8'))
    assert json_body['message'] == 'Origin and destination is required.'

# Test for one missing location, either origin and destination (400)
def test_get_rates_missing_one_location():
    url_params = { 'date_from': '2016-01-01', 'date_to': '2016-01-10', 'origin': 'CNSGH' }

    response = app.test_client().get(f'/rates?{urlencode(url_params)}')

    assert response.status_code == 400
    json_body = json.loads(response.data.decode('utf-8'))
    assert json_body['message'] == 'Origin and destination is required.'

# Test for an invalid port code, either origin and destination (400)
def test_get_rates_invalid_port():
    url_params = { 'date_from': '2016-01-01', 'date_to': '2016-01-10', 'origin': 'XNTNX', 'destination': 'north_europe_main' }

    response = app.test_client().get(f'/rates?{urlencode(url_params)}')

    assert response.status_code == 404
    json_body = json.loads(response.data.decode('utf-8'))
    assert json_body['message'] == 'Origin is not a valid port code or region slug.'

# Test for an invalid region slug, either origin and destination (400)
def test_get_rates_invalid_region():
    url_params = { 'date_from': '2016-01-01', 'date_to': '2016-01-10', 'origin': 'CNSGH', 'destination': 'underwater_atlantis' }

    response = app.test_client().get(f'/rates?{urlencode(url_params)}')

    assert response.status_code == 404
    json_body = json.loads(response.data.decode('utf-8'))
    assert json_body['message'] == 'Destination is not a valid port code or region slug.'

# Test for missing date_to and date_from (must return all entries)
def test_get_rates_no_date_range():
    url_params = {'origin': 'CNSGH', 'destination': 'north_europe_main' }

    response = app.test_client().get(f'/rates?{urlencode(url_params)}')

    assert response.status_code == 200

    json_body = json.loads(response.data.decode('utf-8'))

    # Assertion based on default test (guaranteed 10 days of rates including null)
    assert len(json_body) >= 10 

    # TODO: Do custom assertion (query from DB and compare)?

# Test for missing date_to only (must return date_from to latest date entries)
def test_get_rates_missing_date_to():
    url_params = {'date_from': '2016-01-01', 'origin': 'CNSGH', 'destination': 'north_europe_main' }

    response = app.test_client().get(f'/rates?{urlencode(url_params)}')

    assert response.status_code == 200

    json_body = json.loads(response.data.decode('utf-8'))

    for entry in json_body:
        assert datetime.strptime(url_params['date_from'], DEFAULT_DATE_FORMAT) <= datetime.strptime(entry['day'] , DEFAULT_DATE_FORMAT)

# Test for missing date_from only (must return earliest date to date_to entries)
def test_get_rates_missing_date_from():
    url_params = {'date_to': '2016-01-10', 'origin': 'CNSGH', 'destination': 'north_europe_main' }

    response = app.test_client().get(f'/rates?{urlencode(url_params)}')

    assert response.status_code == 200

    json_body = json.loads(response.data.decode('utf-8'))

    for entry in json_body:
        assert datetime.strptime(url_params['date_to'], DEFAULT_DATE_FORMAT) >= datetime.strptime(entry['day'] , DEFAULT_DATE_FORMAT)


def assert_scoped_dates(response, request_date_from, request_date_to):
    expected_dates = generate_date_range(request_date_from, request_date_to)
    for entry in response:
        assert entry['day'] in expected_dates

def generate_date_range(date_from, date_to):
    start = datetime.strptime(date_from, DEFAULT_DATE_FORMAT)
    end = datetime.strptime(date_to, DEFAULT_DATE_FORMAT)

    date_range = [ start + timedelta(days=d) for d in range(0, (end-start).days + 1) ]

    return [ str(d.date()) for d in date_range ]

