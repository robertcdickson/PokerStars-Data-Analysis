DELETE FROM card_info;
DELETE FROM pre_flop;
DELETE FROM flop;
DELETE FROM turn;
DELETE FROM river;
DELETE FROM general;

SELECT * FROM card_info;
SELECT * FROM flop;

UPDATE pre_flop
    SET "Player Name"= 'Hero'
WHERE "Player Name"='bobsondugnutt11';

UPDATE flop
    SET "Player Name"= 'Hero'
WHERE "Player Name"='bobsondugnutt11';

UPDATE turn
    SET "Player Name"= 'Hero'
WHERE "Player Name"='bobsondugnutt11';

UPDATE river
    SET "Player Name"= 'Hero'
WHERE "Player Name"='bobsondugnutt11';

UPDATE card_info
    SET "Player Name"= 'Hero'
WHERE "Player Name"='bobsondugnutt11';

UPDATE general
    SET "Player Name"= 'Hero'
WHERE "Player Name"='bobsondugnutt11';

UPDATE pre_flop
SET "Facing Pre-Flop 3-Bet" = 'False'
WHERE "Facing Pre-Flop 3-Bet" IS NULL;

UPDATE flop
SET "Flop Final Pot ($)"=NULL
WHERE "Flop Final Pot ($)"=0.0;

UPDATE river
SET "River 3-Bet"='False'
WHERE "River 3-Bet" IS NULL;

UPDATE river
SET "River 3-Bet"='False'
WHERE "River 3-Bet" IS NULL;

UPDATE river
SET "All In"='False'
WHERE "All In" IS NULL