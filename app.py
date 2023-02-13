from flask import Flask, request, abort, make_response, jsonify
from psycopg2 import connect, extras, sql
import logging

import json
import os

from helpers import does_location_exists, get_default_day, is_port_code, construct_query_for_location
from constants import (
    QUERY_EARLIEST_DAY, 
    QUERY_LATEST_DAY, 
    QUERY_AGGREGATED_PRICES,
    QUERY_GENERATED_DATES_GIVEN_RANGE,
    QUERY_DAYS_AND_PRICES
)

app = Flask(__name__)

app.config.from_object('config.Config')
if os.environ.get('ENV') == 'docker':
    app.config.from_object('config.DockerConfig')

handler = logging.FileHandler('app.log')  # Create the file logger
app.logger.addHandler(handler)             # Add it to the built-in logger
app.logger.setLevel(logging.DEBUG)         # Set the log level to debug

def get_db_connection():
    conn = connect(
        host=app.config['DB_HOST'],
        database=app.config['DB_NAME'],
        user=app.config['DB_USER'], 
        password=app.config['DB_PASSWORD'] 
    )
    return conn

@app.route('/', methods=['GET'])
def index():
    return 'Hello World!'

@app.route('/rates', methods=['GET'])
def get_rates():
    args = request.args
    app.logger.debug(f'Request parameters: {json.dumps(args)}')

    # For query string parameters, we assume they are optional
    date_from = args.get('date_from')
    date_to = args.get('date_to')
    origin = args.get('origin')
    destination = args.get('destination')
    
    rates = []

    conn = get_db_connection()
    try:
        # The API is specific only to rates between two locations, thus one cannot be missing
        if not origin or not destination:
            app.logger.error(f'Bad Request: origin={origin} destination={destination}')
            abort(400, 'Origin and destination is required.')

        with conn.cursor() as cur:
            # We check if origin exists in database (for port code or region slug)
            if not does_location_exists(cur, origin):
                app.logger.error(f'Not Found: origin={origin}')
                abort(404, 'Origin is not a valid port code or region slug.')

            # We check if destination exists in database (for port code or region slug)
            if not does_location_exists(cur, destination):
                app.logger.error(f'Not Found: origin={destination}')
                abort(404, 'Destination is not a valid port code or region slug.')

            # We assume that if the date_from is not provided, we get earliest day available
            if not date_from:
                date_from = get_default_day(cur, QUERY_EARLIEST_DAY)
                app.logger.debug(f'Default earliest date is used: {date_from}')
            
            # We assume that if the date_to is not provided, we get latest day available
            if not date_to:
                date_to = get_default_day(cur, QUERY_LATEST_DAY)
                app.logger.debug(f'Default latest date is used: {date_to}')

        sql_origin = sql.Literal(origin) if is_port_code(origin) else construct_query_for_location(origin)
        sql_destination = sql.Literal(destination) if is_port_code(destination) else construct_query_for_location(destination)
        sql_date_from = sql.Literal(date_from)
        sql_date_to = sql.Literal(date_to)

        sql_prices = sql.SQL(QUERY_AGGREGATED_PRICES).format(sql_origin, sql_destination, sql_date_from, sql_date_to)
        sql_dates = sql.SQL(QUERY_GENERATED_DATES_GIVEN_RANGE).format(sql_date_from, sql_date_to)

        with conn.cursor(cursor_factory = extras.RealDictCursor) as cur:
            query = sql.SQL(QUERY_DAYS_AND_PRICES).format(sql_dates, sql_prices)
            app.logger.debug(f'Query to database: {query.as_string(conn)}')
            cur.execute(query)
        
            result = json.dumps(cur.fetchall(), default=str)    # NOTE: "default=str" is a hackaround for datetime conversion
            rates = json.loads(result)                          # NOTE: Hackaround for converting json string into dict in conjunction to above
    finally:
        conn.close()

    app.logger.debug(f'Database result: {rates}')
    for r in rates:
        count = r['price_count']
        if count is not None and count < 3:
            r['average_price'] = None
        
        average_price = r['average_price']
        if average_price is not None:
            r['average_price'] = round(float(r['average_price']))  # NOTE: Hackaround for converting string numbers to int in conjunction to above
        
        del r['price_count']

    return rates


@app.errorhandler(400)
def custom_bad_request(error):
    return make_response(jsonify({ 'message': error.description }), 400)

@app.errorhandler(404)
def custom_not_found(error):
    return make_response(jsonify({ 'message': error.description }), 404)


if __name__ == '__main__':
    app.run()


