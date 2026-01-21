SELECT *
FROM t100_cleaned;

SELECT *
FROM db1b_merged;

# since db1b is a 10% sample of the price data, not all flights from the t100 data would be listed. Hence checking the availablity of db1b data for t100 routes.alter

#cleaning useless data, seats 0 and passengers 0 is probably a maintainance flight/ferry flight. As a thumb rule, removing lfights with less than 20 pax as they m,ight be a ferry flight or a maintainance flight.
SELECT *
FROM t100_cleaned
WHERE SEATS < 20 OR PASSENGERS < 20;

DELETE
FROM t100_cleaned
WHERE SEATS < 20 OR PASSENGERS < 20;

-- EXPLORING THE DATA FROM T100 DATASET

SELECT *
FROM t100_cleaned
ORDER BY PASSENGERS DESC;

#summing up pax, seats, dept performed, flight time and avg of distance, grouping by origin, dest and aircraft type.

CREATE TEMPORARY TABLE Traffic_Temp AS
SELECT ORIGIN, DEST, AIRCRAFT_TYPE, 
		SUM(DEPARTURES_PERFORMED) AS Total_Departures, 
        SUM(SEATS) AS Annual_Seat_Capacity,
        SUM(PASSENGERS) AS Annual_Pax_Volume,
        SUM(RAMP_TO_RAMP) AS Total_Flight_Time,
        AVG(DISTANCE) AS Distance_Miles
FROM t100_cleaned
WHERE UNIQUE_CARRIER = 'UA'
GROUP BY ORIGIN, DEST, AIRCRAFT_TYPE;
        
#creating a CTE with rolling total to check if there is any repeated values. 
        
WITH duplicate_cte AS
(
SELECT *, ROW_NUMBER () OVER (PARTITION BY ORIGIN, DEST) AS row_num
FROM Traffic_Temp
)
SELECT *
FROM duplicate_cte
WHERE row_num > 1;

-- EXPLORING THE DB1B PRICE TABLES

SELECT *
FROM db1b_merged
ORDER BY PAX_WEIGHTING ASC;

SELECT COUNT(*)
FROM db1b_merged
WHERE MARKET_FARE = 0
ORDER BY MARKET_FARE ASC;

#found an anomaly in the market fare section, low values and decimal numbers are present. This is definetly an outlier.

#Assuming these low values are frequent flyer miles redeemed. Exploring the data further. Dividing mkt fare into tiers such as standard fare, low fare and award ticket. 

#upon research, when you redeem miles for a free ticket, you are charged $5.60 each way for the september 11 security fee, which explains the numbers. Or it can be employee travel or smtn like that.

SELECT 
    CASE 
        WHEN MARKET_FARE BETWEEN 0 AND 10 THEN 'Award_Ticket_Tier ($0-$10)'
        WHEN MARKET_FARE BETWEEN 10.01 AND 50 THEN 'Ultra_Low_Fare ($10-$50)'
        ELSE 'Standard_Fare (>$50)'
    END as Fare_Category,
    COUNT(*) as Ticket_Count,
    AVG(MARKET_FARE) as Avg_Price_In_Category
FROM db1b_merged
GROUP BY 1
ORDER BY 2 DESC;

#keeping these values in the dataset as it is part of the operations, not an erroneous figure.

-- Creating Price Temp table
DROP TEMPORARY TABLE IF EXISTS Price_Temp;

CREATE TEMPORARY TABLE Price_Temp
SELECT ORIGIN, DEST, SUM(MARKET_FARE * PAX_WEIGHTING) / SUM(PAX_WEIGHTING) AS Avg_Fare
FROM db1b_merged
WHERE MARKET_FARE>= 0
GROUP BY ORIGIN, DEST;

-- NOW CREATING A FINAL NEW TABLE TO MERGE THESE 2 TEMP TABLES.

SELECT *
FROM Traffic_Temp;

SELECT *
FROM Price_Temp;


#merged table

CREATE TABLE Final_Route_Data AS
SELECT 
    t.ORIGIN,
    t.DEST,
    t.AIRCRAFT_TYPE,
    t.Total_Departures,
    t.Annual_Seat_Capacity,
	t.Annual_Pax_Volume,
    t.Total_Flight_Time,
    t.Distance_Miles,
    p.Avg_Fare
FROM Traffic_Temp t
LEFT JOIN Price_Temp p
	ON TRIM(t.ORIGIN) = TRIM(p.ORIGIN)
    AND TRIM(t.DEST) = (p.DEST)
;

# checking data before moving on to calculations

-- Checking for impossible passenger counts
SELECT * 
FROM Final_Route_Data
WHERE Annual_Pax_Volume > Annual_Seat_Capacity;

-- Checking for bad time data (flying 0 minutes or impossible speeds)
SELECT *,
    (Distance_Miles / (Total_Flight_Time / 60)) as Speed_MPH
FROM Final_Route_Data
WHERE Total_Flight_Time <= 0 
   OR (Distance_Miles / (Total_Flight_Time / 60)) > 700;
   
-- What % of our traffic is missing price data?
SELECT 
    COUNT(*) as Total_Routes,
    SUM(CASE WHEN Avg_Fare IS NULL THEN 1 ELSE 0 END) as Missing_Price_Count,
    (SUM(CASE WHEN Avg_Fare IS NULL THEN 1 ELSE 0 END) / COUNT(*)) * 100 as Percent_Missing
FROM Final_Route_Data;

# out of 8054 routes flows, 736 has no price data, that is 9.14% missing

-- EXPORTING CSV
SELECT *
FROM Final_Route_Data;



-- form 41 p5.2 operational costs database excploration
SELECT *
FROM form41_p52
ORDER BY TOTAL_AIR_HOURS DESC;

#total air hours is in thousands, so value * 1000

CREATE TABLE Aircraft_Costs AS
SELECT AIRCRAFT_TYPE, SUM(TOT_AIR_OP_EXPENSES) / SUM(TOTAL_AIR_HOURS) AS Hourly_Op_Cost, SUM(TOTAL_AIR_HOURS) *1000 AS Total_Fleet_Hours
FROM form41_p52
WHERE UNIQUE_CARRIER = 'UA' AND TOTAL_AIR_HOURS > 0
GROUP BY 1
HAVING SUM(TOTAL_AIR_HOURS) > 1.0;

# checking duplicate entries per aircraft type
SELECT *, ROW_NUMBER () OVER (PARTITION BY AIRCRAFT_TYPE) AS row_num		
FROM Aircraft_Costs;

SELECT DISTINCT Aircraft_type, Hourly_Op_Cost
FROM Aircraft_Costs;

-- MERGING COSTS AND TRAFFIC DATA

CREATE TABLE Final_Route_Financials AS
SELECT 
    m.*, c.Hourly_Op_Cost as Hourly_Cost
FROM Final_Route_Data m
LEFT JOIN Aircraft_Costs c 
    ON m.AIRCRAFT_TYPE = c.AIRCRAFT_TYPE;

SELECT * FROM Final_Route_Financials ;

-- ADDING AIRCRAFT NAME INTO THE DATA FOR READABILITY

SELECT DISTINCT AIRCRAFT_TYPE
FROM Final_Route_Financials;

SELECT *
FROM aircraft_types;

#CHECKING JOIN COMPATIBILITY
SELECT DISTINCT f.Aircraft_type, a.LONG_NAME Aircraft_Name
FROM Final_Route_Financials f
LEFT JOIN aircraft_types a
    ON f.Aircraft_type = a.AC_TYPEID;

#ADDING THE NAME INTO THE DATASET
ALTER TABLE Final_Route_Financials
ADD COLUMN Aircraft_Name VARCHAR(255);

UPDATE Final_Route_Financials f
JOIN aircraft_types a
    ON f.Aircraft_Type = a.AC_TYPEID
SET Aircraft_Name = a.LONG_NAME;

#moving the column position for readability
ALTER TABLE Final_Route_Financials
MODIFY Aircraft_Name VARCHAR(255) AFTER AIRCRAFT_TYPE;

SELECT *,
FROM Final_Route_Financials
ORDER BY 1,2;

SELECT COUNT(*)
FROM Final_Route_Financials
WHERE Avg_Fare is null;

SELECT *
FROM Final_Route_Financials;

-- Accounting for Landing Costs. Data is unclear but costs are determined by takeoff weight.

SELECT DISTINCT Aircraft_type, Aircraft_name
FROM Final_Route_Financials;

SELECT *
FROM Final_Route_Financials;

ALTER TABLE Final_Route_Financials
ADD COLUMN Landing_Costs VARCHAR(255);

UPDATE Final_Route_Financials
SET Landing_Costs = CASE 
						WHEN Aircraft_Type IN (627, 637) THEN 2000 
						WHEN Aircraft_Type IN (626, 624) THEN 1500 
						WHEN Aircraft_Type IN (887, 889, 837) THEN 1200
						ELSE 550 
					END;


