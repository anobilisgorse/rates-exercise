from app import app

from urllib.parse import urlencode
from datetime import datetime, timedelta
import json

def test_index_route():
    response = app.test_client().get('/')

    assert response.status_code == 200
    assert response.data.decode('utf-8') == 'Hello World!'

def test_get_rates():
    url_params = { 'date_from': '2016-01-01', 'date_to': '2016-01-10', 'origin': 'CNSGH', 'destination': 'north_europe_main' }

    response = app.test_client().get(f'/rates?{urlencode(url_params)}')
    json_body = json.loads(response.data.decode('utf-8'))

    assert_scoped_dates(json_body, url_params['date_from'], url_params['date_to'])

    date_map = { entry['day']: entry['average_price'] for entry in json_body }

    assert date_map['2016-01-01'] == 1112
    assert date_map['2016-01-02'] == 1112
    assert date_map['2016-01-03'] is None


def assert_scoped_dates(response, request_date_from, request_date_to):
    expected_dates = generate_date_range(request_date_from, request_date_to)
    for entry in response:
        assert entry['day'] in expected_dates

def generate_date_range(date_from, date_to):
    start = datetime.strptime(date_from, '%Y-%m-%d')
    end = datetime.strptime(date_to, '%Y-%m-%d')

    date_range = [ start + timedelta(days=d) for d in range(0, (end-start).days + 1) ]

    return [ str(d.date()) for d in date_range ]

