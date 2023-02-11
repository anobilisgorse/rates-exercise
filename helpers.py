from psycopg2 import sql
from constants import QUERY_PORTS_GIVEN_LOCATION, QUERY_REGION_MAP

def get_default_day(cursor, query_string):
    cursor.execute(query_string)
    (default_date) = cursor.fetchone()
    return str(default_date)

# TODO: Might fail if new data does not follow 5-digit upper case standard
def is_port_code(location):
    location = str(location)
    return len(location) <= 5 and location.isupper()

def construct_query_for_location(location):
    sql_slug = sql.Literal(location)
    return sql.SQL(QUERY_PORTS_GIVEN_LOCATION).format(sql.SQL(QUERY_REGION_MAP), sql_slug, sql_slug, sql_slug)
    