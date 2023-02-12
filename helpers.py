from psycopg2 import sql
from constants import DEFAULT_DATE_FORMAT, QUERY_PORTS_GIVEN_LOCATION, QUERY_REGION_MAP

def get_default_day(cursor, query_string):
    cursor.execute(query_string)
    (default_date, ) = cursor.fetchone()
    return default_date.strftime(DEFAULT_DATE_FORMAT)

# NOTE: Assuming 5-digit upper case standard, if new data does not abide to this code will cause issue
def is_port_code(location):
    location = str(location)
    return len(location) <= 5 and location.isupper()

def construct_query_for_location(location):
    sql_slug = sql.Literal(location)
    sql_regions = sql.SQL(QUERY_REGION_MAP).format(sql_slug)
    return sql.SQL(QUERY_PORTS_GIVEN_LOCATION).format(sql_regions)

# NOTE: Brute force approach involving three-degrees left join of regions
# def construct_query_for_location(location):
#     sql_slug = sql.Literal(location)
#     return sql.SQL(QUERY_PORTS_GIVEN_LOCATION).format(sql.SQL(QUERY_REGION_MAP), sql_slug, sql_slug, sql_slug)

    