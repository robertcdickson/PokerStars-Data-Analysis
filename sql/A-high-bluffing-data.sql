/* The goal of this SQL file is to look at data where there is to generate a table of data where all hands
   satisfy the following conditions

   - Player is not Hero (i.e. looking at the pool)
   - Hand reaches showdown
   - 2 players in hand
   - A single raise and call pre-flop
   - Ace on flop
   */

UPDATE pre_flop
SET "Facing Pre-Flop 3-Bet" = 'False'
WHERE "Facing Pre-Flop 3-Bet" IS NULL;

SELECT COUNT("Facing Pre-Flop 3-Bet")
FROM pre_flop
GROUP BY "Facing Pre-Flop 3-Bet";

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
             1)                                                                       AS "Called Size Flop (% Pot)",
       f."Flop Final Pot ($)",
        g."Winning Rankings",
        g."Winning Hands"
FROM card_info AS c

         INNER JOIN pre_flop AS pf ON pf."Player Name" = c."Player Name" AND pf."Game Code" = c."Game Code"
         INNER JOIN flop AS f ON f."Player Name" = c."Player Name" AND f."Game Code" = c."Game Code"
         INNER JOIN turn AS t ON t."Player Name" = c."Player Name" AND t."Game Code" = c."Game Code"
         INNER JOIN river AS r ON r."Player Name" = c."Player Name" AND r."Game Code" = c."Game Code"
         INNER JOIN general AS g ON g."Player Name" = c."Player Name" AND g."Game Code" = c."Game Code"

WHERE c."Player Name" != 'Hero'
  AND (c."Flop Card 1" LIKE 'A%'
    OR
       c."Flop Card 2" LIKE 'A%'
    OR
       c."Flop Card 3" LIKE 'A%')
  AND pf."Facing Pre-Flop 3-Bet" = 'False'
AND pf."Pre-Flop Raise"='True';

/*                         */
SELECT "Best Ranking", count("Best Ranking")
FROM card_info AS c

         INNER JOIN pre_flop AS pf ON pf."Player Name" = c."Player Name" AND pf."Game Code" = c."Game Code"
         INNER JOIN flop AS f ON f."Player Name" = c."Player Name" AND f."Game Code" = c."Game Code"
         INNER JOIN turn AS t ON t."Player Name" = c."Player Name" AND t."Game Code" = c."Game Code"
         INNER JOIN river AS r ON r."Player Name" = c."Player Name" AND r."Game Code" = c."Game Code"
         INNER JOIN general AS g ON g."Player Name" = c."Player Name" AND g."Game Code" = c."Game Code"

WHERE c."Player Name" != 'Hero'
  AND (c."Flop Card 1" LIKE 'A%'
    OR
       c."Flop Card 2" LIKE 'A%'
    OR
       c."Flop Card 3" LIKE 'A%')
  AND pf."Facing Pre-Flop 3-Bet" = 'False'
AND pf."Pre-Flop Raise"='True'
AND f."Flop Raise"='True'
AND t."Turn Raise"='True'
AND r."River Raise"='True'

GROUP BY "Best Ranking";