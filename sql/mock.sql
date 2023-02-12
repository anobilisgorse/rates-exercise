-- -- (OBSOLETE) Join regions to self to get parentmost (brute force, will fail if relationship exceeds 3 degrees)
-- SELECT r1.slug as slug,
--     r1.name as name,
--     r2.slug as parent_slug,
--     r3.slug as root_slug
-- FROM regions r1
--     LEFT JOIN regions r2 ON r1.parent_slug = r2.slug
--     LEFT JOIN regions r3 ON r2.parent_slug = r3.slug;

-- -- (OBSOLETE) Get ports given region (brute force, filtering by slug/parent_slug/root_slug)
-- SELECT 
--     -- 	joined_regions.root_slug as root_port_slug,
--     -- 	joined_regions.parent_slug as parent_port_slug,
--     -- 	ports.parent_slug as port_slug,
--     -- 	joined_regions.name as port_slug_name,
--     -- 	ports.name as port_name,
--     ports.code as port_code
-- FROM ports
--     INNER JOIN (
--         SELECT r1.slug as slug,
--             r1.name as name,
--             r2.slug as parent_slug,
--             r3.slug as root_slug
--         FROM regions r1
--             LEFT JOIN regions r2 ON r1.parent_slug = r2.slug
--             LEFT JOIN regions r3 ON r2.parent_slug = r3.slug
--     ) joined_regions ON ports.parent_slug = joined_regions.slug
-- WHERE ports.parent_slug = 'north_europe_main'
--     OR joined_regions.parent_slug = 'north_europe_main'
--     OR joined_regions.root_slug = 'north_europe_main';


-- Get descendant regions using recursive query
WITH RECURSIVE region_tree AS (
    SELECT * FROM regions WHERE slug = 'china_main'
    UNION ALL
    SELECT r.* 
		FROM regions AS r 
		JOIN region_tree AS rt 
		ON r.parent_slug = rt.slug
)
SELECT slug FROM region_tree 


-- Get ports given regions
SELECT 
    --  joined_regions.root_slug as root_port_slug,
    --  joined_regions.parent_slug as parent_port_slug,
    --  ports.parent_slug as port_slug,
    --  joined_regions.name as port_slug_name,
    --  ports.name as port_name,
        ports.code as port_code
    FROM ports
    WHERE ports.parent_slug IN (
        WITH RECURSIVE region_tree AS (
            SELECT * FROM regions WHERE slug = 'north_europe_main'
            UNION ALL
            SELECT r.* 
                FROM regions AS r 
                JOIN region_tree AS rt 
                ON r.parent_slug = rt.slug
        )
        SELECT slug FROM region_tree
    )

-- Get prices given origin, destination and date range
SELECT * FROM prices 
	WHERE orig_code IN ('CNSGH') 
	AND dest_code IN (
            SELECT 
        --  joined_regions.root_slug as root_port_slug,
        --  joined_regions.parent_slug as parent_port_slug,
        --  ports.parent_slug as port_slug,
        --  joined_regions.name as port_slug_name,
        --  ports.name as port_name,
            ports.code as port_code
        FROM ports
        WHERE ports.parent_slug IN (
            WITH RECURSIVE region_tree AS (
                SELECT * FROM regions WHERE slug = 'north_europe_main'
                UNION ALL
                SELECT r.* 
                    FROM regions AS r 
                    JOIN region_tree AS rt 
                    ON r.parent_slug = rt.slug
            )
            SELECT slug FROM region_tree
        )
    ) 
	AND (day BETWEEN '2016-01-01' AND '2016-01-10')


-- Generate list of days given date range
SELECT day::date
FROM generate_series(timestamp '2016-01-01', '2016-01-10', '1 day') day;

-- full join query
SELECT a.day,
    b.avg,
    b.count
FROM (
        SELECT day::date
        FROM generate_series(timestamp '2016-01-01', '2016-01-10', '1 day') day
    ) a
    LEFT JOIN (
        SELECT day,
            avg(price),
            count(price)
        FROM prices
        WHERE orig_code IN ('CNSGH') 
        AND dest_code IN (
                SELECT 
            --  joined_regions.root_slug as root_port_slug,
            --  joined_regions.parent_slug as parent_port_slug,
            --  ports.parent_slug as port_slug,
            --  joined_regions.name as port_slug_name,
            --  ports.name as port_name,
                ports.code as port_code
            FROM ports
            WHERE ports.parent_slug IN (
                WITH RECURSIVE region_tree AS (
                    SELECT * FROM regions WHERE slug = 'north_europe_main'
                    UNION ALL
                    SELECT r.* 
                        FROM regions AS r 
                        JOIN region_tree AS rt 
                        ON r.parent_slug = rt.slug
                )
                SELECT slug FROM region_tree
            )
        ) 
        AND (day BETWEEN '2016-01-01' AND '2016-01-10')
        GROUP BY day
    ) b ON a.day = b.day
ORDER BY a.day ASC;