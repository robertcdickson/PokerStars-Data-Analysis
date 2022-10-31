/* This file is used to practice different aspects of SQL. It gives a (very long) way of taking two columns each with
   a string representation of a playing card and returns a column with string of the (ordered) cards and if they are suited
   or not */

SELECT *
FROM card_info;

ALTER TABLE card_info
    ADD COLUMN "Player Card 1 Value" VARCHAR(2),
    ADD COLUMN "Player Card 2 Value" VARCHAR(2);

UPDATE card_info
SET "Player Card 1 Value"=SUBSTRING("Player Card 1", 0, 2),
    "Player Card 2 Value"=SUBSTRING("Player Card 2", 0, 2)
WHERE "Player Card 1 Value" IS NOT NULL;

UPDATE card_info
SET "Player Card 1 Value"= (CASE
                                WHEN card_info."Player Card 1 Value" = 'A' THEN '14'
                                WHEN card_info."Player Card 1 Value" = 'K' THEN '13'
                                WHEN card_info."Player Card 1 Value" = 'Q' THEN '12'
                                WHEN card_info."Player Card 1 Value" = 'J' THEN '11'
                                WHEN card_info."Player Card 1 Value" = 'T' THEN '10'
                                ELSE card_info."Player Card 1 Value"
    END)
WHERE "Player Card 1 Value" IS NOT NULL;

UPDATE card_info
SET "Player Card 2 Value"= (CASE
                                WHEN card_info."Player Card 2 Value" = 'A' THEN '14'
                                WHEN card_info."Player Card 2 Value" = 'K' THEN '13'
                                WHEN card_info."Player Card 2 Value" = 'Q' THEN '12'
                                WHEN card_info."Player Card 2 Value" = 'J' THEN '11'
                                WHEN card_info."Player Card 2 Value" = 'T' THEN '10'
                                ELSE card_info."Player Card 2 Value"
    END)
WHERE "Player Card 2 Value" IS NOT NULL;

ALTER TABLE card_info
    ALTER COLUMN "Player Card 1 Value" TYPE INTEGER
        USING card_info."Player Card 1 Value"::INTEGER;

ALTER TABLE card_info
    ALTER COLUMN "Player Card 2 Value" TYPE INTEGER
        USING card_info."Player Card 2 Value"::INTEGER;

UPDATE card_info
SET "Player Card 1 Value"=card_info."Player Card 2 Value",
    "Player Card 2 Value"=card_info."Player Card 1 Value"
WHERE card_info."Player Card 1 Value" < "Player Card 2 Value";

ALTER TABLE card_info
    ALTER COLUMN "Player Card 1 Value" TYPE VARCHAR(2);

ALTER TABLE card_info
    ALTER COLUMN "Player Card 2 Value" TYPE VARCHAR(2);

UPDATE card_info
SET "Player Card 1 Value"= (CASE
                                WHEN card_info."Player Card 1 Value" = '14' THEN 'A'
                                WHEN card_info."Player Card 1 Value" = '13' THEN 'K'
                                WHEN card_info."Player Card 1 Value" = '12' THEN 'Q'
                                WHEN card_info."Player Card 1 Value" = '11' THEN 'J'
                                WHEN card_info."Player Card 1 Value" = '10' THEN 'T'
                                ELSE card_info."Player Card 1 Value"
    END)
WHERE "Player Card 1 Value" IS NOT NULL;

UPDATE card_info
SET "Player Card 2 Value"= (CASE
                                WHEN card_info."Player Card 2 Value" = '14' THEN 'A'
                                WHEN card_info."Player Card 2 Value" = '13' THEN 'K'
                                WHEN card_info."Player Card 2 Value" = '12' THEN 'Q'
                                WHEN card_info."Player Card 2 Value" = '11' THEN 'J'
                                WHEN card_info."Player Card 2 Value" = '10' THEN 'T'
                                ELSE card_info."Player Card 2 Value"
    END)
WHERE "Player Card 2 Value" IS NOT NULL;

ALTER TABLE card_info
    ADD COLUMN "Player Cards" VARCHAR(3);

UPDATE card_info
SET "Player Cards"= (CASE
                         WHEN SUBSTRING("Player Card 1", 0, 2) = SUBSTRING("Player Card 2", 0, 2)
                             THEN CONCAT("Player Card 1 Value", "Player Card 2 Value")
                         WHEN SUBSTRING("Player Card 1", 1) = SUBSTRING("Player Card 2", 1)
                             THEN CONCAT("Player Card 1 Value", "Player Card 2 Value", 's')
                         WHEN SUBSTRING("Player Card 1", 1) != SUBSTRING("Player Card 2", 1)
                             THEN CONCAT("Player Card 1 Value", "Player Card 2 Value", 'o')
    END)
WHERE "Player Card 2 Value" IS NOT NULL;


SELECT *
FROM card_info;