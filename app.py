from flask import Flask, request
import psycopg2, psycopg2.extras

import json

app = Flask(__name__)

def get_db_connection():
    # TODO: Put in config?
    conn = psycopg2.connect(host='localhost',
                            database='postgres',    
                            user='postgres',        
                            password='ratestask')
    return conn

@app.route('/', methods=['GET'])
def index():
    return 'Hello World!'

@app.route('/rates', methods=['GET'])
def get_rates():
    args = request.args
    date_from = args.get('date_from')
    date_to = args.get('date_to')
    origin = args.get('origin')
    destination = args.get('destination')

    #TODO: Do parameter check
    #TODO: Sanitize parameters (eg. remove "" if any)
 
    rates = []

    #TODO: Do optimization? (eg. return early etc)

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as cur:
            query = query_days_and_prices(origin, destination, date_from, date_to)
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

# TODO: Move to separate file
def query_generated_dates_given_range(date_from, date_to):
    return f'''
        SELECT day::date 
            FROM generate_series(timestamp '{date_from}', '{date_to}', '1 day') day
    '''

def query_days_and_prices(origin, destination, date_from, date_to):
    return f'''
        SELECT dates.day as day, aggregated_prices.average_price as average_price, aggregated_prices.price_count as price_count
        FROM ({query_generated_dates_given_range(date_from, date_to)}) dates
        LEFT JOIN ({query_aggregated_prices(origin, destination, date_from, date_to)}) aggregated_prices
        ON dates.day = aggregated_prices.day
        ORDER BY day ASC
    '''

def query_aggregated_prices(origin, destination, date_from, date_to):
    return f'''
        SELECT day, avg(price) as average_price, count(price) as price_count FROM prices 
            WHERE orig_code IN ({query_ports_given_location(origin)}) 
            AND dest_code IN ({query_ports_given_location(destination)})
            AND (day BETWEEN '{date_from}' AND '{date_to}')
            GROUP BY day
    '''

# TODO: Might fail if new data does not follow 5-digit upper case standard
def is_port_code(location):
    location = str(location)
    return len(location) <= 5 and location.isupper()

def query_ports_given_location(location):
    return f"'{location}'" if is_port_code(location) else f'''
        SELECT 
        -- 	joined_regions.root_slug as root_port_slug,
        -- 	joined_regions.parent_slug as parent_port_slug,
        -- 	ports.parent_slug as port_slug,
        -- 	joined_regions.name as port_slug_name,
        -- 	ports.name as port_name,
            ports.code as port_code
        FROM ports 
        INNER JOIN 
            ({query_region_map()}) joined_regions
                ON ports.parent_slug = joined_regions.slug 
        WHERE ports.parent_slug='{location}' 
        OR joined_regions.parent_slug='{location}' 
        OR joined_regions.root_slug='{location}'
    '''

# TODO: Can be optimized by creating new schema instead?
# TODO: Hackaround, will fail if new data will cause nesting references that exceeds 3 degrees (eg. new -> parent_slug -> grand_parent_slug -> root_slug)
def query_region_map():
    return '''
        SELECT
            r1.name as name, 
            r1.slug as slug, 
            r2.slug as parent_slug, 
            r3.slug as root_slug 
        FROM regions r1 
        LEFT JOIN regions r2 
            ON r1.parent_slug = r2.slug 
        LEFT JOIN regions r3 
            ON r2.parent_slug = r3.slug
    '''

if __name__ == '__main__':
    app.run()


