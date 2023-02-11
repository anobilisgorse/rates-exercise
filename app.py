from flask import Flask, request, abort, make_response, jsonify
# import logging
from psycopg2 import connect, extras, sql

import json

from helpers import get_default_day, is_port_code, construct_query_for_location
from constants import (QUERY_EARLIEST_DAY, 
    QUERY_LATEST_DAY, 
    QUERY_REGION_MAP,
    QUERY_PORTS_GIVEN_LOCATION,
    QUERY_AGGREGATED_PRICES,
    QUERY_GENERATED_DATES_GIVEN_RANGE,
    QUERY_DAYS_AND_PRICES)


# logging.basicConfig(filename='record.log', level=logging.DEBUG)
app = Flask(__name__)

def get_db_connection():
    # TODO: Put in config?
    conn = connect(host='localhost',
                            database='postgres',    
                            user='postgres',        
                            password='ratestask')
    return conn

@app.route('/', methods=['GET'])
def index():
    return 'Hello World!'

#TODO: Do logging?
@app.route('/rates', methods=['GET'])
def get_rates():
    args = request.args

    # For query string parameters, we assume they are optional
    date_from = args.get('date_from')
    date_to = args.get('date_to')
    origin = args.get('origin')
    destination = args.get('destination')

    #TODO: Sanitize parameters (eg. remove "" if any)
    
    rates = []

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # We assume that if the date_from is not provided, we get earliest day available
            if not date_from:
                date_from = get_default_day(cur, QUERY_EARLIEST_DAY)
            
            # We assume that if the date_to is not provided, we get latest day available
            if not date_to:
                date_to = get_default_day(cur, QUERY_LATEST_DAY)

        # We assume that we can get all rates of all origins and destination, but not if one is unknown and other is known
        # (eg. origin is provided but destination is not provided)
        if (origin and not destination) or (not origin and destination):
            abort(400, "Provide both origin or destination or none at all.")

        sql_origin = sql.Literal(origin) if is_port_code(origin) else construct_query_for_location(origin)
        sql_destination = sql.Literal(destination) if is_port_code(destination) else construct_query_for_location(destination)
        sql_date_from = sql.Literal(date_from)
        sql_date_to = sql.Literal(date_to)

        sql_prices = sql.SQL(QUERY_AGGREGATED_PRICES).format(sql_origin, sql_destination, sql_date_from, sql_date_to)
        sql_dates = sql.SQL(QUERY_GENERATED_DATES_GIVEN_RANGE).format(sql_date_from, sql_date_to)

        with conn.cursor(cursor_factory = extras.RealDictCursor) as cur:
            query = sql.SQL(QUERY_DAYS_AND_PRICES).format(sql_dates, sql_prices)
            print(query.as_string(conn))
            cur.execute(query)
        
            result = json.dumps(cur.fetchall(), default=str)    # TODO: "default=str" is a hackaround for datetime conversion; rework into a more elegant way of fetching results
            rates = json.loads(result)                          # TODO: Hackaround for converting json string into dict in conjunction to above; needs rework also
    finally:
        conn.close()

    for r in rates:
        count = r['price_count']
        if count is not None and count < 3:
            r['average_price'] = None
        
        average_price = r['average_price']
        if average_price is not None:
            r['average_price'] = round(float(r['average_price']))  # TODO: Hackaround for converting string numbers to int in conjunction to above; needs rework also
        
        del r['price_count']

    return rates


@app.errorhandler(400)
def custom_bad_request(error):
    return make_response(jsonify({ 'message': error.description }), 400)


if __name__ == '__main__':
    app.run()


