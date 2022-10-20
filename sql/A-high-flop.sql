/* The goal of this SQL file is to look at data where there is an Ace on the flop in my database. The easiest first
   way to analyse this is when showdown is reached and both players cards are known */

SELECT c.*, f.*
FROM card_info AS c
         INNER JOIN flop AS f ON f."Player Name" = c."Player Name" AND f."Game Code" = c."Game Code"
         INNER JOIN general AS g ON g."Player Name" = c."Player Name" AND g."Game Code" = c."Game Code"
WHERE c."Player Name" != 'Hero'
  AND (c."Flop Card 1" LIKE 'A%'
    OR
       c."Flop Card 2" LIKE 'A%'
    OR
       c."Flop Card 3" LIKE 'A%')
AND c."Three-Of-A-Kind Street"='Flop';

/* Q1. How often do other players call a flop bet OOP when there is an Ace on the flop? */

/* To answer this we need to know how many A-flops there are with player data that does not include hero*/

SELECT g."Position",
       f."Flop Card 1",
       f."Flop Card 2",
       f."Flop Card 3",
       f."Turn Card",
       f."River Card",
       CONCAT(SUBSTRING(c."Player Card 1", 0, 2), SUBSTRING(c."Player Card 2", 0, 2)) AS "Cards",
       C."Best Ranking",
       f."Check Flop",
       f."Called Flop Raise",
       ROUND(f."Called Flop Raise size" / (f."Flop Final Pot ($)" - 2 * f."Called Flop Raise size"),
             1)                                                                       AS "Called Size (% Pot)",
        f."Flop Final Pot ($)"
FROM card_info AS c
         INNER JOIN flop AS f ON f."Player Name" = c."Player Name" AND f."Game Code" = c."Game Code"
         INNER JOIN general AS g ON g."Player Name" = c."Player Name" AND g."Game Code" = c."Game Code"
WHERE c."Player Name" != 'Hero'
  AND (c."Flop Card 1" LIKE 'A%'
    OR
       c."Flop Card 2" LIKE 'A%'
    OR
       c."Flop Card 3" LIKE 'A%')
  AND f."Facing Flop Raise" = 'True'
  AND f."Called Flop Raise" = 'True';

/* Then want to see those hands which a player check-calls*/

SELECT g."Position",
       f."Flop Card 1",
       f."Flop Card 2",
       f."Flop Card 3",
       f."Turn Card",
       f."River Card",
       CONCAT(SUBSTRING(c."Player Card 1", 0, 2), SUBSTRING(c."Player Card 2", 0, 2)) AS "Cards",
       C."Best Ranking",
       f."Check Flop",
       f."Called Flop Raise",
       ROUND(f."Called Flop Raise size" / (f."Flop Final Pot ($)" - 2 * f."Called Flop Raise size"),
             1)                                                                       AS "Called Size (% Pot)",
        f."Flop Final Pot ($)"
FROM card_info AS c
         INNER JOIN flop AS f ON f."Player Name" = c."Player Name" AND f."Game Code" = c."Game Code"
         INNER JOIN general AS g ON g."Player Name" = c."Player Name" AND g."Game Code" = c."Game Code"
WHERE c."Player Name" != 'Hero'
  AND (c."Flop Card 1" LIKE 'A%'
    OR
       c."Flop Card 2" LIKE 'A%'
    OR
       c."Flop Card 3" LIKE 'A%')
  AND f."Facing Flop Raise" = 'True'
  AND f."Called Flop Raise" = 'True';

/* GROUP BY */
SELECT c."Best Ranking", 100 * COUNT("Best Ranking") / SUM(count("Best Ranking")) OVER()
FROM card_info AS c
         INNER JOIN flop AS f ON f."Player Name" = c."Player Name" AND f."Game Code" = c."Game Code"
         INNER JOIN general AS g ON g."Player Name" = c."Player Name" AND g."Game Code" = c."Game Code"
WHERE c."Player Name" != 'Hero'
  AND (c."Flop Card 1" LIKE 'A%'
    OR
       c."Flop Card 2" LIKE 'A%'
    OR
       c."Flop Card 3" LIKE 'A%')
  AND f."Facing Flop Raise" = 'True'
  AND f."Flop Re-raise" = 'True'
GROUP BY c."Best Ranking";


SELECT *
FROM card_info AS c
         INNER JOIN flop AS f ON f."Player Name" = c."Player Name" AND f."Game Code" = c."Game Code"
         INNER JOIN general AS g ON g."Player Name" = c."Player Name" AND g."Game Code" = c."Game Code"
;

SELECT *
FROM flop;

/* Select relevant data*/
SELECT c."Game Code",
       c."Player Name",
       c."Flop Card 1",
       c."Flop Card 2",
       c."Flop Card 3",
       c."Turn Card",
       c."River Card",
       CONCAT(SUBSTRING(c."Player Card 1", 0, 2), SUBSTRING(c."Player Card 2", 0, 2)) AS "Cards",
       C."Best Ranking",
       f."Check Flop",
       f."Flop Raise",
       ROUND(f."Called Flop Raise size" / (f."Flop Final Pot ($)" - 2 * f."Called Flop Raise size"),
             1)                                                                       AS "Called Size (% Pot)"

FROM card_info AS C
         INNER JOIN flop AS f ON f."Game Code" = C."Game Code" AND f."Player Name" = C."Player Name"
         INNER JOIN general AS g ON g."Player Name" = c."Player Name" AND g."Game Code" = c."Game Code"

WHERE (C."Player Name" != 'Hero'
    AND
       f."Called Flop Raise" = 'True')
  AND (C."Flop Card 1" LIKE 'A%'
    OR
       C."Flop Card 2" LIKE 'A%'
    OR
       C."Flop Card 3" LIKE 'A%')
;

/* Grouped rankings found for A-high flops found at showdown */
SELECT "Best Ranking", COUNT(*) AS "Count", COUNT(*) * 100 / SUM(COUNT(*)) OVER () AS "%"

FROM card_info AS C
         INNER JOIN flop AS f ON f."Game Code" = C."Game Code" AND f."Player Name" = C."Player Name"
         INNER JOIN general AS g ON g."Player Name" = c."Player Name" AND g."Game Code" = c."Game Code"

WHERE (C."Player Name" != 'Hero'
    AND
       f."Called Flop Raise" = 'True')
  AND (C."Flop Card 1" LIKE 'A%'
    OR
       C."Flop Card 2" LIKE 'A%'
    OR
       C."Flop Card 3" LIKE 'A%')

GROUP BY "Best Ranking"
;

/* Get bet sizes on all flops with A */
SELECT ROUND("Flop Raise Size" / ("Flop Final Pot ($)" - 2 * "Flop Raise Size"),
             1) AS "Bet Size Called (% of Pot)"
FROM flop
WHERE "Flop Raise Size" IS NOT NULL;

/* Select relevant data*/
SELECT ROUND(f."Called Flop Raise size" / (f."Flop Final Pot ($)" - 2 * f."Called Flop Raise size"),
             1) AS "Bet Size Called (% of Pot)",
       100 * COUNT(ROUND(f."Called Flop Raise size" / (f."Flop Final Pot ($)" - 2 * f."Called Flop Raise size"), 1)) /
       SUM(COUNT(ROUND(f."Called Flop Raise size" / (f."Flop Final Pot ($)" - 2 * f."Called Flop Raise size"), 1)))
       OVER ()  AS "% of Counts"

FROM card_info AS c
         INNER JOIN flop AS f ON f."Game Code" = c."Game Code" AND f."Player Name" = c."Player Name"
         INNER JOIN general AS g ON g."Player Name" = c."Player Name" AND g."Game Code" = c."Game Code"

WHERE (C."Player Name" != 'Hero'
    AND
       f."Called Flop Raise" = 'True')
  AND (C."Flop Card 1" LIKE 'A%'
    OR
       C."Flop Card 2" LIKE 'A%'
    OR
       C."Flop Card 3" LIKE 'A%')
GROUP BY "Bet Size Called (% of Pot)"
;