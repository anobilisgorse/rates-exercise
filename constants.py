DEFAULT_DATE_FORMAT = '%Y-%m-%d'

QUERY_EARLIEST_DAY = 'SELECT MIN(day) FROM prices'

QUERY_LATEST_DAY = 'SELECT MAX(day) FROM prices'

QUERY_GENERATED_DATES_GIVEN_RANGE = '''
    SELECT day::date 
        FROM generate_series(timestamp {}, {}, '1 day') day
'''

QUERY_DAYS_AND_PRICES = '''
    SELECT dates.day as day, aggregated_prices.average_price as average_price, aggregated_prices.price_count as price_count
    FROM ({}) dates
    LEFT JOIN ({}) aggregated_prices
    ON dates.day = aggregated_prices.day
    ORDER BY day ASC
'''

QUERY_AGGREGATED_PRICES = '''
    SELECT day, avg(price) as average_price, count(price) as price_count FROM prices 
        WHERE orig_code IN ({}) 
        AND dest_code IN ({})
        AND (day BETWEEN {} AND {})
        GROUP BY day
'''

QUERY_PORTS_GIVEN_LOCATION = '''
    SELECT 
    -- 	joined_regions.root_slug as root_port_slug,
    -- 	joined_regions.parent_slug as parent_port_slug,
    -- 	ports.parent_slug as port_slug,
    -- 	joined_regions.name as port_slug_name,
    -- 	ports.name as port_name,
        ports.code as port_code
    FROM ports
    WHERE ports.parent_slug IN ({})
'''

# # NOTE: Uses inner join
# QUERY_PORTS_GIVEN_LOCATION = '''
#     SELECT 
#     -- 	joined_regions.root_slug as root_port_slug,
#     -- 	joined_regions.parent_slug as parent_port_slug,
#     -- 	ports.parent_slug as port_slug,
#     -- 	joined_regions.name as port_slug_name,
#     -- 	ports.name as port_name,
#         ports.code as port_code
#     FROM ports 
#     INNER JOIN 
#          ({}) joined_regions
#          ON ports.parent_slug = joined_regions.slug
# '''

QUERY_REGION_MAP = '''
    WITH RECURSIVE region_tree AS (
        SELECT * FROM regions WHERE slug = {}
        UNION ALL
        SELECT r.* 
            FROM regions AS r 
            JOIN region_tree AS rt 
            ON r.parent_slug = rt.slug
    )
    SELECT slug FROM region_tree
'''

# # NOTE: Brute force approach involving three-degrees left join of regions
# QUERY_PORTS_GIVEN_LOCATION = '''
#     SELECT 
#     -- 	joined_regions.root_slug as root_port_slug,
#     -- 	joined_regions.parent_slug as parent_port_slug,
#     -- 	ports.parent_slug as port_slug,
#     -- 	joined_regions.name as port_slug_name,
#     -- 	ports.name as port_name,
#         ports.code as port_code
#     FROM ports 
#     INNER JOIN 
#         ({}) joined_regions
#             ON ports.parent_slug = joined_regions.slug 
#     WHERE ports.parent_slug={} 
#     OR joined_regions.parent_slug={} 
#     OR joined_regions.root_slug={}
# '''

# # NOTE: Brute force approach involving three-degrees left join of regions, will fail if new data will cause nesting references that exceeds 3 degrees (eg. new -> parent_slug -> grand_parent_slug -> root_slug)
# QUERY_REGION_MAP = '''
#     SELECT
#         r1.name as name, 
#         r1.slug as slug,    
#         r2.slug as parent_slug, 
#         r3.slug as root_slug 
#     FROM regions r1 
#     LEFT JOIN regions r2 
#         ON r1.parent_slug = r2.slug 
#     LEFT JOIN regions r3 
#         ON r2.parent_slug = r3.slug
# '''

