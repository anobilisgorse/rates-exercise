-- join regions to get parentmost (hackaround, will fail if relationship exceeds 3 degrees)
SELECT r1.slug as slug, r1.name as name, r2.slug as parent_slug, r3.slug as root_slug FROM regions r1 LEFT JOIN regions r2 ON r1.parent_slug = r2.slug LEFT JOIN regions r3 ON r2.parent_slug = r3.slug;

-- get ports given region (slug/parent_slug/root_slug)
SELECT 
-- 	joined_regions.root_slug as root_port_slug,
-- 	joined_regions.parent_slug as parent_port_slug,
-- 	ports.parent_slug as port_slug,
-- 	joined_regions.name as port_slug_name,
-- 	ports.name as port_name,
	ports.code as port_code
FROM ports INNER JOIN 
(SELECT r1.slug as slug, r1.name as name, r2.slug as parent_slug, r3.slug as root_slug FROM regions r1 
 LEFT JOIN regions r2 ON r1.parent_slug = r2.slug 
 LEFT JOIN regions r3 ON r2.parent_slug = r3.slug) joined_regions
ON ports.parent_slug = joined_regions.slug 
WHERE ports.parent_slug='north_europe_main' 
OR joined_regions.parent_slug='north_europe_main' 
OR joined_regions.root_slug='north_europe_main';

-- test
-- SELECT * FROM prices 
-- 	WHERE orig_code IN ('CNSGH') 
-- 	AND dest_code IN (SELECT 
-- 	-- 	joined_regions.root_slug as root_port_slug,
-- 	-- 	joined_regions.parent_slug as parent_port_slug,
-- 	-- 	ports.parent_slug as port_slug,
-- 	-- 	joined_regions.name as port_slug_name,
-- 	-- 	ports.name as port_name,
-- 		ports.code as port_code
-- 	FROM ports INNER JOIN 
-- 	(SELECT r1.slug as slug, r1.name as name, r2.slug as parent_slug, r3.slug as root_slug FROM regions r1 
-- 	 LEFT JOIN regions r2 ON r1.parent_slug = r2.slug 
-- 	 LEFT JOIN regions r3 ON r2.parent_slug = r3.slug) joined_regions
-- 	ON ports.parent_slug = joined_regions.slug 
-- 	WHERE ports.parent_slug='north_europe_main' 
-- 	OR joined_regions.parent_slug='north_europe_main' 
-- 	OR joined_regions.root_slug='north_europe_main') 
-- 	AND day = '2016-01-04'
	
-- generate days given range
SELECT day::date 
FROM   generate_series(timestamp '2016-01-01', '2016-01-10', '1 day') day;


SELECT a.day, b.avg, b.count FROM
(SELECT day::date FROM generate_series(timestamp '2016-01-01', '2016-01-10', '1 day') day) a
LEFT JOIN
(SELECT day, avg(price), count(price) FROM prices 
	WHERE orig_code IN ('CNSGH') 
	AND dest_code IN (SELECT 
	-- 	joined_regions.root_slug as root_port_slug,
	-- 	joined_regions.parent_slug as parent_port_slug,
	-- 	ports.parent_slug as port_slug,
	-- 	joined_regions.name as port_slug_name,
	-- 	ports.name as port_name,
		ports.code as port_code
	FROM ports INNER JOIN 
	(SELECT r1.slug as slug, r1.name as name, r2.slug as parent_slug, r3.slug as root_slug FROM regions r1 
	 LEFT JOIN regions r2 ON r1.parent_slug = r2.slug 
	 LEFT JOIN regions r3 ON r2.parent_slug = r3.slug) joined_regions
	ON ports.parent_slug = joined_regions.slug 
	WHERE ports.parent_slug='north_europe_main' 
	OR joined_regions.parent_slug='north_europe_main' 
	OR joined_regions.root_slug='north_europe_main')
	AND (day BETWEEN '2016-01-01' AND '2016-01-10')
	GROUP BY day) b on a.day = b.day order by a.day desc;
	
	
	
	SELECT dates.day as day, aggregated_prices.average_price as average_price, aggregated_prices.price_count as price_count
        FROM (
        SELECT day::date 
            FROM generate_series(timestamp '2016-01-01', '2016-01-10', '1 day') day
    ) dates
        LEFT JOIN (
        SELECT day, avg(price) as average_price, count(price) as price_count FROM prices 
            WHERE orig_code IN ('CNSGH') 
            AND dest_code IN (
        SELECT 
        --      joined_regions.root_slug as root_port_slug,
        --      joined_regions.parent_slug as parent_port_slug,
        --      ports.parent_slug as port_slug,
        --      joined_regions.name as port_slug_name,
        --      ports.name as port_name,
            ports.code as port_code
        FROM ports 
        INNER JOIN 
            (
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
    ) joined_regions
                ON ports.parent_slug = joined_regions.slug 
        WHERE ports.parent_slug='north_europe_main"'
        OR joined_regions.parent_slug='north_europe_main"'
        OR joined_regions.root_slug='north_europe_main"'
    )
            AND (day BETWEEN '2016-01-01' AND '2016-01-10')
            GROUP BY day
    ) aggregated_prices
        ON dates.day = aggregated_prices.day
        ORDER BY day DESC

