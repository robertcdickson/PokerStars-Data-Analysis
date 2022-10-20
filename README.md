# Poker
This repo contains python code to work with poker data. 
A basic poker game is implemented which can be used to run simulated games. 
The PokerStarsCollection class allows for working with pokerstars
output files which can then be passed to the poker game to simulate real game scenarios.

# PokerStarsCollection Module
The PokerStarsCollection module contains two classes, `PokerStarsCollection` and
`PokerGame`. The `PokerStarsCollection` Object assimilates a whole poker 
session consisting of individual `PokerStarGame` objects.

```python
from pokerstars import PokerStarsCollection
poker_session = PokerStarsCollection(file="../example_data/multigame_example_anonymized.txt")
```

From this collection, each game can analysed. Games are stored in a dictionary called `games_data` and accessed as 
follows.

```python
for game in poker_session.games_data.hand_values():
    print(game)
```

Each game is then printed out in its `__str__` format

```jupyter
Poker Game #0
-------------------------
Winners: Sleve_McDichael 
Winning Cards: Not Shown
Table Cards: 9s 6h 7h
-------------------------

Poker Game #1
------------------------
Winners: Willie_Dustice 
Winning Cards: Not Shown
Table Cards: Not Dealt
------------------------

Poker Game #2
------------------------
Winners: Bobson_Dugnutt 
Winning Cards: Not Shown
Table Cards: Not Dealt
------------------------

Poker Game #3
--------------------------
Winners: Karl_Dandleton 
Winning Cards: Not Shown
Table Cards: Ks 6c 7h 6d
--------------------------

...
```

Each PokerGame has attributes attached to it with the whole game saved as a pandas dataframe.
One attribute of a PokerGame is a list of winners. This allows for easy filtering of games in a collection.

```python
for game in poker_session.games_data.hand_values():
    if "Bobson_Dugnutt" in game.winners:
        print(game)
```

Which prints each game that Bobson_Dugnutt wins.

```jupyter
Poker Game #2
------------------------
Winners: Bobson_Dugnutt 
Winning Cards: Not Shown
Table Cards: Not Dealt
------------------------

Poker Game #4
--------------------------
Winners: Bobson_Dugnutt 
Winning Cards: Not Shown
Table Cards: Qh 7c Ks 4h
--------------------------

Poker Game #5
------------------------
Winners: Bobson_Dugnutt 
Winning Cards: Not Shown
Table Cards: 7h Js 3h
------------------------
```
