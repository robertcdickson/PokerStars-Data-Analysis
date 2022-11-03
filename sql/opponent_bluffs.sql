/*

The goal of this file is to get all relevant data from opponents that involve betting the river. With this dataset,
where some are labeled and some unlabeled, I want to get a training and testing set to make a binary classifier
to determine if a bet is a bluff or a value bet

*/

/* ################################################################################################################## */

SELECT "All In", "Best Ranking", COUNT("Best Ranking")
FROM card_info AS c
         INNER JOIN river AS r ON r."Player Name" = c."Player Name" AND r."Game Code" = c."Game Code"
WHERE c."Player Name" != 'Hero'
  AND r."River Raise" = 'True'
  AND r."River 3-Bet" = 'False'
GROUP BY "Best Ranking", "All In";

SELECT ROUND(r."River Raise Size" / t."Turn Final Pot ($)", 2),
       COUNT(ROUND(r."River Raise Size" / t."Turn Final Pot ($)", 2))
FROM card_info AS c
         INNER JOIN turn AS t ON t."Player Name" = c."Player Name" AND t."Game Code" = c."Game Code"
         INNER JOIN river AS r ON r."Player Name" = c."Player Name" AND r."Game Code" = c."Game Code"
WHERE c."Player Name" != 'Hero'
  AND r."River Raise" = 'True'
  AND r."River 3-Bet" = 'False'
GROUP BY ROUND(r."River Raise Size" / t."Turn Final Pot ($)", 2);


COPY(
SELECT c."Player Name",
       c."Flop Card 1",
       c."Flop Card 2",
       c."Flop Card 3",
       c."Turn Card",
       c."River Card",
       c."Player Cards",
       c."Suited Hand",
       c."Suited Hand Suit",
       c."Best Ranking",
       f."Flop Raise",
       t."Turn Raise",
       t."Check Turn",
       t."Turn Raise",
       r."River 3-Bet",
       r."River Raise Size",
       t."Turn Final Pot ($)"                                  AS "Initial River Pot ($)",
       ROUND(t."Turn Raise Size" / f."Flop Final Pot ($)", 2)  AS "Bet Size Turn (fraction of pot)",
       ROUND(r."River Raise Size" / t."Turn Final Pot ($)", 2) AS "Bet Size River (fraction of pot)",
       g."Big Blind",
       r."All In",
       r."All In Street"

FROM card_info AS c

         INNER JOIN pre_flop AS pf ON pf."Player Name" = c."Player Name" AND pf."Game Code" = c."Game Code"
         INNER JOIN flop AS f ON f."Player Name" = c."Player Name" AND f."Game Code" = c."Game Code"
         INNER JOIN turn AS t ON t."Player Name" = c."Player Name" AND t."Game Code" = c."Game Code"
         INNER JOIN river AS r ON r."Player Name" = c."Player Name" AND r."Game Code" = c."Game Code"
         INNER JOIN general AS g ON g."Player Name" = c."Player Name" AND g."Game Code" = c."Game Code"

WHERE c."Player Name" != 'Hero'
  AND r."River Raise" = 'True'
  AND r."River 3-Bet" = 'False')
TO '/tmp/bluff_data.csv' DELIMITER ',' CSV HEADER
;

SELECT *
FROM general;