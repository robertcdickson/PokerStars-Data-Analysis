import copy
import re

import numpy as np
import pandas as pd
from typing import List

from poker_main import *
from data_catagories import full_column_headings
from board_analysis import SingleBoardAnalysis

"""
TODO:

Draws on flop and turn
Rankings on flop and turn (currently only done on river)
Relative position in hand

"""


class PokerStarsGame(object):
    """
    An object containing all data related to a Pokerstars game.
    """

    def __init__(
            self,
            game_text: List,
            data: pd.DataFrame,
            table_cards: List[Card],
            winners: List,
            winning_hands: List = None,
            winning_ranking: str = None,
            hero: str = "bobsondugnutt11",
            game_index: int = 0,
            hero_cards: list = None,
    ):
        """

        Args:
            game_text (list):
                List containing each of a PokerStars game
            data (Dataframe):
                A dataframe with different attributes of the game
            table_cards (list):
                List of Cards on table
            winners (list):
                List of the winners of the game
            winning_hands (list):
                List of hands that won the game
            winning_ranking (str):
                Highest ranking of cards that won
            hero: (str)
                Name of player defined as hero
            game_index (int):
                An index used to track PokerStarsCollection games
            hero_cards: (list)
                A list of hero's cards

        """
        self._suits = {"c": "clubs", "s": "spades", "d": "diamonds", "h": "hearts"}

        self._values = {
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "T": 10,
            "J": 11,
            "Q": 12,
            "K": 13,
            "A": 14,
        }

        self.deck = [Card(value + suit) for suit in self._suits for value in self._values]

        if data is None:
            self.data = None  # self.get_data_from_text()

        self.data = data
        self.game_index = game_index
        self.game_text = game_text
        self.winners = winners
        self.winning_hands = winning_hands
        self.winning_rankings = winning_ranking

        self.hero = hero
        self._hero_cards = hero_cards

        self.flop_cards = None
        self.turn_card = None
        self.river_card = None

        self.flop_card_1 = None
        self.flop_card_2 = None
        self.flop_card_3 = None

        if table_cards:
            self.table_cards = table_cards
            if len(table_cards) >= 3:
                self.flop_cards = table_cards[0:3]
            if len(table_cards) >= 4:
                self.turn_card = table_cards[3].string
            if len(table_cards) == 5:
                self.river_card = table_cards[4].string
        else:
            self.table_cards = None

        if self.flop_cards:
            self.flop_card_1 = self.flop_cards[0].string
            self.flop_card_2 = self.flop_cards[1].string
            self.flop_card_3 = self.flop_cards[2].string

        self._big_blind = self.get_blind("BB")
        self._small_blind = self.get_blind("SB")
        self.chip_leader = self.data["General"].index[
            self.data["General"]["Chips ($)"] == self.data["General"]["Chips ($)"].max()
            ].to_list()

        self.player_cards_text = self.get_player_cards()

        self.player_names = None
        self.player_final_action = None

        self.final_pot, self.rake = self.get_final_pot()

        self._all_column_labels = full_column_headings

        if "Zoom" in self.game_text[0]:
            self.game_type = "Zoom"
            self.game_code = self.game_text[0].split("#")[1].split(":")[0]
            self.stakes = self.game_text[0].split("(")[1].split(")")[0]
            self._big_blind_size = float(self.stakes.split("/")[1].strip("$"))
            self.data["General"]["Chips (BB)"] = self.data["General"]["Chips ($)"] / self._big_blind_size
            self.date = self.game_text[0].split("-")[1].split("[")[0].split(" ")[1]
            self.time = self.game_text[0].split("-")[1].split("[")[0].split(" ")[2]
            self.max_players = self.game_text[1].split("'")[2].split(" ")[1]
            self.table_name = self.game_text[1].split("'")[1]
        else:
            self.game_type = "Normal"
            self.game_code = self.game_text[0].split("#")[1].split(":")[0]
            self.stakes = self.game_text[0].split("(")[1].split(")")[0].split(" ")[0]
            self._big_blind_size = float(self.stakes.split("/")[1].strip("$").split()[0])
            self.data["General"]["Chips (BB)"] = self.data["General"]["Chips ($)"] / self._big_blind_size
            self.date = self.game_text[0].split("-")[1].split("[")[0].split(" ")[1]
            self.time = self.game_text[0].split("-")[1].split("[")[0].split(" ")[2]
            self.max_players = self.game_text[1].split("'")[2].split(" ")[1]
            self.table_name = self.game_text[1].split("'")[1]

        self._values_for_all_df = {
            "Game Code": self.game_code,
            "Flop Card 1": self.flop_card_1,
            "Flop Card 2": self.flop_card_2,
            "Flop Card 3": self.flop_card_3,
            "Turn Card": self.turn_card,
            "River Card": self.river_card,
        }

        self._values_for_general_df = {
            "Game Type": self.game_type,
            "Game Code": self.game_code,
            "Stakes": self.stakes,
            "Date": self.date,
            "Time": self.time,
            "Max Players": self.max_players,
            "Rake": self.rake,
            "Final Pot": self.final_pot,
            "Table Name": self.table_name,
            "Flop Card 1": self.flop_card_1,
            "Flop Card 2": self.flop_card_2,
            "Flop Card 3": self.flop_card_3,
            "Turn Card": self.turn_card,
            "River Card": self.river_card,
            # "Winners": str(self.winners),
            "Winning Hands": str(self.winning_hands),
            "Winning Rankings": str(self.winning_rankings),
        }

    def reorder_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Reorders columns according to data_categories.py file
        Args:
            df (DataFrame):
                Dataframe to reorder
        Returns:
            df[new_column_labels] (DataFrame):
                Reordered dataframe

        """
        new_column_labels = [x for x in self._all_column_labels if x in df.columns]
        return df[new_column_labels]

    def get_blind(self, size: str) -> list:
        """
        Function to get big or small blind

        Args:
            size (str):
                Describes blind type. Options: "BB" or "SB"

        Returns:
            blind (list):
                List of indices where the position is equal to blind type

        """
        blind = self.data["General"].index[self.data["General"]["Position"] == size].to_list()
        return blind

    def translate_hand(self, hand: List[str]) -> List[tuple]:
        """
        Translates hand from pokerstars output format to list of tuples

        Args:
            hand (list):
                List of cards a player has

        Returns:
            translated_hand (list):
                List of tuples of different cards
        """
        translated_hand = [
            (int(self._values[card[0]]), self._suits[card[1]]) for card in hand
        ]
        return translated_hand

    def get_player_cards(self) -> List[Card]:
        """
        Function to get the hero players hand

        Returns:
            new_cards (list):
                List of Card objects in Hero's hand

        """
        for line in self.game_text:
            if "Dealt" in line and self.hero in line:
                cards = line.split("[")[-1].rstrip("]\n").split()
                new_cards = [Card(x) for x in cards]
                return new_cards

    def get_final_pot(self) -> float:
        """
        Gets the final pot value

        Returns:
            pot (float):
                Final pot size in dollars
        """
        for line in self.game_text:
            if "Total pot" in line:
                pot = float(line.split("|")[0].split()[2].strip("()$"))
                rake = float(line.split("|")[1].split()[1].strip("()$"))
                return pot, rake

    def get_data_from_text(self):
        """
        Function to get all data from a text file. NOT IMPLEMENTED

        """
        pass

    def get_full_data(self) -> pd.DataFrame:
        """
        Gets the full DataFrame for a game

        Returns:
            new_df (DataFrame):
                full DataFrame for the game
        """
        new_df = self.data
        for df_key in new_df:
            if df_key == "General":
                for key, value in self._values_for_general_df.items():
                    new_df[df_key][key] = value
            else:
                for key, value in self._values_for_all_df.items():
                    new_df[df_key][key] = value

            # reorders columns based on formatting in data_categories.py
            if type(new_df[df_key]) == pd.DataFrame:
                self.reorder_columns(new_df[df_key])
        return new_df

    def simulate_game(
            self, players=None, n=100, use_table_cards=True, table_card_length=5
    ) -> (dict, dict, dict):
        """
        A function that runs a simulation for n games to see how likely a hero is to win against other hands

        Args:
            players (list):
                List of players involved in hand
            n (int):
                Number of simulations to run
            use_table_cards (bool):
                If True, the table cards associated with the hand are used
            table_card_length (int):
                Number of table cards to include in the simulation. Only works if "use_table_cards" is True

        Returns:
            winners_dict (dict):
                A dictionary containing the win percentage for each player
            ties_dict (dict):
                A dictionary containing the tie percentage for each player
            table_cards_dict (dict):
                A dictionary containing the table cards of each simulation

        """
        # set up
        winners_dict = {k: 0 for k in [x.name for x in players]}
        ties_dict = {k: 0 for k in [x.name for x in players]}
        table_cards_dict = {}

        # used cards are cards that can no longer come out of the deck
        used_cards = list(itertools.chain([y for x in players for y in x.cards]))

        for player in players:
            player.hand_ranking = []

        # simulates the game n times
        for i in range(n):
            current_players = copy.deepcopy(players)
            ranking_dict = {}
            # get ranking of each hand with the set of table cards
            if use_table_cards:
                rankings = BoardAnalysis(current_players, self.table_cards)
            else:
                cards = copy.deepcopy(self.deck)
                for card in used_cards:
                    cards.remove(card)
                table_cards = random.sample(cards, table_card_length)
                rankings = BoardAnalysis(current_players, table_cards)

            # get a list of winners in hand
            winning_list = rankings.winners
            table_cards_dict[i] = self.table_cards

            # determine if single winner of if there was a draw
            for winner in winning_list:
                if len(winning_list) > 1:
                    ties_dict[winner.name] += 1
                else:
                    winners_dict[winner.name] += 1

        for key, value in winners_dict.items():
            winners_dict[key] = 100 * value / n
        for key, value in ties_dict.items():
            ties_dict[key] = 100 * value / n

        return winners_dict, ties_dict, table_cards_dict

    def __str__(self):

        print_winners = ""
        for winner in self.winners:
            print_winners += f"{winner} "
        print_winners.lstrip(" ")

        print_winning_hands = ""
        for winning_hand in self.winning_hands:
            print_winning_hands += winning_hand
        print_winning_hands.lstrip(" ")

        if print_winning_hands == "":
            print_winning_hands = "Not Shown"

        if self.table_cards is None:
            print_table_cards = "Not dealt"
        else:
            print_table_cards = self.table_cards

        line = "-" * max(
            [
                len(y)
                for y in [
                "Winners: " + print_winners,
                "Winning Cards: " + f"{print_table_cards}",
                "Table Cards: " + print_winning_hands,
            ]
            ]
        )
        return (
                f"Poker Game #{self.game_index}\n"
                + line
                + "\n"
                + f"Winners: {print_winners}\n"
                  f"Winning Cards: {print_winning_hands}\n"
                  f"Table Cards: {print_table_cards}\n" + line + "\n"
        )


class PokerStarsCollection(object):
    def __init__(
            self,
            file: str,
            working_dir: str,
            encoding: str = "ISO-8859-14",
            hero: str = "Bobson_Dugnutt",
            write_files: bool = False,
            max_games: str = None,
    ):
        """
        A collection of PokerStarsGame objects

        Args:
            file (str):
                File to read in
            working_dir (str):
                Current working directory where script is run
            encoding (str):
                Character encoding. As files are typically saved on a Windows system, the default is "ISO-8859-14"
            hero (str):
                The PokerStars username of the player
            write_files (bool):
                Determines if individual game files are to be written when data file is split. Default: False
            max_games (int):
                Max number of games to be processed.
        """

        self.rake = 0.0
        self._suits = {"c": "clubs", "s": "spades", "d": "diamonds", "h": "hearts"}

        self._values = {
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "T": 10,
            "J": 11,
            "Q": 12,
            "K": 13,
            "A": 14,
        }

        self.seats = {
            1: "BTN",
            2: "SB",
            3: "BB",
            4: "LJ",
            5: "HJ",
            6: "CO",
        }

        self.file = file
        self.working_dir = working_dir
        self.hero = hero
        self._hero_cards = None

        self._search_dict = {
            "Pre-Flop": "HOLE CARDS",
            "Flop": "FLOP",
            "Turn": "TURN",
            "River": "RIVER",
            "Showdown": "SHOW DOWN",
        }

        if not max_games:
            self.max_games = 0
        else:
            self.max_games = max_games

        self._encoding = encoding
        self._games_text = self.process_file(split_files=write_files)
        self.games_data = {}

        self._all_column_labels = full_column_headings

        self._small_blind = 0.0
        self._big_blind = 0.0
        self._small_blind_player = None
        self._big_blind_player = None

        i = 0
        for key, game in self._games_text.items():
            if "Tournament" in game[0] or "Hold'em" not in game[0]:  # ignoring tournament hands for the moment
                continue
            if not i % 100:
                print(f"Game {i}")
            if self.max_games and i >= self.max_games:
                break
            self.games_data[key] = self.read_pokerstars_file(lines=game, game_index=i)
            i += 1

        self.winners = [game.winners[0] for game in self.games_data.values()]
        self.winner_count = Counter(self.winners)

        self.full_data = {

        }

        for game in self.games_data.values():
            data = game.get_full_data()
            for key in data.keys():
                if key == "summary" or key == "Showdown":
                    continue
                if key not in self.full_data.keys():
                    self.full_data[key] = []
                self.full_data[key].append(data[key])

        for key in self.full_data:
            self.full_data[key] = pd.concat(self.full_data[key])
            self.full_data[key] = self.full_data[key].reset_index(drop=True)
            self.full_data[key] = self.reorder_columns(self.full_data[key])

        self.positions = None

    def process_file(self, split_files: bool = False) -> dict:
        """

        Splits a PokerStars file in to individual games

        Args:
            split_files (bool):
                Determines if file is to be split into individual files
        Returns:
            files_dict (dict):
                Dict of all games in data file

        """

        # a function that chunks a file of poker stars hands into individual poker_session
        files_dict = {}
        file_number = 0

        # open file with pokerstars data in it
        with open(self.file, "r", encoding=self._encoding) as rf:

            line_marker = 0

            # start and write markers need for starting/stopping of file chunk
            start = False
            write = False

            for line in rf.readlines():
                # at present can only look at hands from cash games
                if (
                        "PokerStarsCollection Hand" in line
                        or "PokerStars Zoom Hand" in line
                        or "PokerStars Hand" in line
                ):
                    start = True
                    write = True
                    files_dict[file_number] = []
                    if split_files:
                        wf = open(f"{self.working_dir}/hand_{file_number}.txt", "w")

                if start:
                    if write:
                        files_dict[file_number].append(line)
                        if split_files:
                            wf.write(line)

                    if line == "\n":
                        line_marker += 1

                    # if 2 \n tokens found then the poker game is finished and the writing of the file ends
                    if line_marker == 2:
                        line_marker = 0
                        write = False
                        if split_files:
                            wf.close()
                        file_number += 1

        print("Finished file splitting into individual games")
        return files_dict

    @staticmethod
    def read_hand(hand: list, hand_regex: re.Pattern):
        # reads in a hand given a hand regex
        return hand_regex.findall(hand)[0].strip("[]").split()

    def reorder_columns(self, df):
        """
        Reorders a Dataframe's columns in to the order specificed in self._all_column_labels

        Args:
            df (Dataframe):
                Pandas dataframe to reorder

        Returns:
            df (Dataframe):
                The reordered dataframe
        """

        new_column_labels = [
            x for x in self._all_column_labels if x in df.columns.to_list()
        ]
        df = df[new_column_labels]

        return df

    def translate_hand(self, hand):
        # translates hand from pokerstars output format to list of tuples
        return [(self._values[card[0]], self._suits[card[1]]) for card in hand]

    def read_hand_file(self, file):

        """
        Reads a PokerStars file and finds any cards in that file

        Args:
            file (str):
                file name

        Returns:
            translated_hand (tuple):
                A hand translated in to a tuple format
            translated_board (list)
                A list of translated cards on the board

        """
        # define regex for later reading
        hand_regex = re.compile("\[.*\]")

        # Dealt and Board are the only two parts of pokerstars file that include cards (besides shown which isn't
        # implemented yet
        with open(file, "r") as rf:
            for line in rf.readlines():
                if "Dealt" in line:
                    hand = self.read_hand(line, hand_regex)
                    translated_hand = self.translate_hand(hand)
                if "Board" in line:
                    board = self.read_hand(line, hand_regex)
                    translated_board = self.translate_hand(board)

        return translated_hand, translated_board

    @staticmethod
    def get_button_seat(self, file):
        # returns the index of the seat currently on the button
        with open(file, "r") as rf:
            return int(re.search("#\d", rf.readlines()[1]).group().strip("#"))

    @staticmethod
    def split_game_to_events(file, lines):
        # takes in a pokerstars game and returns a dictionary with different pieces of data
        data_dicts = {}
        if file:
            with open(file, "r") as rf:
                key = "HEADER"
                data_dicts[key] = []
                for line in rf.readlines():
                    if "***" in line:
                        if any(x in line for x in ["RIVER"]):
                            table_cards = (
                                re.search(r"\[.*\]", line)
                                .group()
                                .replace("[", "")
                                .replace("]", "")
                            )
                            data_dicts["TABLE_CARDS"] = table_cards
                        key = re.search(r"\*\*\*.*\*\*\*", line).group().strip("* ")
                        data_dicts[key] = []
                    else:
                        data_dicts[key].append(line)
                return data_dicts
        if lines:
            key = "HEADER"
            data_dicts[key] = []
            for line in lines:
                if "*** " in line and "said" not in line:
                    if any(x in line for x in ["RIVER"]):
                        table_cards = (
                            re.search(r"\[.*\]", line)
                            .group()
                            .replace("[", "")
                            .replace("]", "")
                        )
                        data_dicts["TABLE_CARDS"] = table_cards
                    key = re.search(r"\*\*\*.*\*\*\*", line).group().strip("* ")
                    data_dicts[key] = []
                else:
                    data_dicts[key].append(line)
            return data_dicts

    def read_pre_deal_lines(self, player_list):
        # Function that reads data from the pre-deal section of the game
        stakes = None
        data_dict = {"Player Name": [], "Seat Number": [], "Chips ($)": []}

        button_seat = int(re.search("#\d", player_list[1]).group().strip("#"))
        stakes = []
        self._small_blind = 0
        self._big_blind = 0
        for line in player_list:
            if line.startswith("PokerStars "):
                stakes = line.split("(")[1]
                stakes = stakes.split(")")[0]
                stakes = stakes.split("/")
                self._small_blind = stakes[0].lstrip("$")
                self._big_blind = stakes[1].lstrip("$").split()[0]

            player = re.findall(":.*\(", line)

            if player and "chips" in line:
                # get hero name and number of chips
                line_list = line.split(" ")

                # get different pieces of data pre dealing
                seat_number = int(line_list[1].strip(":"))
                player_name = player[0][2:-2]
                chips = float(
                    line_list[-4].strip("($")
                )

                data_dict["Player Name"].append(player_name)
                data_dict["Seat Number"].append(seat_number)
                data_dict["Chips ($)"].append(chips)

            if "posts small blind" in line:
                self._small_blind_player = line.rsplit(":")[0].replace(" ", "")
            if "posts big blind" in line:
                self._big_blind_player = line.rsplit(":")[0].replace(" ", "")

        # renumber seat numbers for ordering of play
        new_seat_order = [i for i in range(1, len(data_dict["Seat Number"]) + 1)]
        data_dict["Play Order"] = []
        new_button = new_seat_order[data_dict["Seat Number"].index(button_seat)]

        data_dict["Play Order"] = [
            seat - new_button + len(data_dict["Seat Number"])
            if int(seat) - new_button < 0
            else seat - new_button
            if int(seat) - new_button > 0
            else len(data_dict["Seat Number"])
            for seat in new_seat_order
        ]

        data_dict["Betting Order"] = [
            i - 2 if i - 2 > 0 else i - 2 + len(data_dict["Play Order"])
            for i in data_dict["Play Order"]
        ]
        data_dict["Is Big Blind"] = [
            True if j == 2 else False for j in data_dict["Play Order"]
        ]
        data_dict["Is Small Blind"] = [
            True if j == 1 else False for j in data_dict["Play Order"]
        ]

        data_df = pd.DataFrame(data_dict).set_index(["Player Name"])
        data_df["Small Blind"] = float(self._small_blind)
        data_df["Big Blind"] = float(self._big_blind)

        conditions = [
            (data_df["Is Small Blind"] == True),
            (data_df["Is Big Blind"] == True),
            (data_df["Is Small Blind"] == False) & (data_df["Is Big Blind"] == False),
        ]
        values = [float(self._small_blind), float(self._big_blind), 0.0]
        data_df["Added to Pot Pre-Deal"] = np.select(conditions, values)

        return data_df

    def read_betting_action(self, lines_list, play_phase=None):
        """
        Function that gets data from a single play phase
        Args:
            lines_list (list):
                A list of lines in the play phase
            play_phase (str):
                Betting round. Values allowed are "Pre-Flop", "Flop", "Turn" and "River"

        Returns:
            df (dataframe):
                All data from this play phase

        """
        data = {}
        general_data = {}
        pot = 0.0

        all_in_raise = False

        # pre-flop there has been a bet due to big blind
        if play_phase == "Pre-Flop":
            number_of_raises = 1
            number_of_calls = 1  # this may be problematic later
        else:
            number_of_raises = 0
            number_of_calls = 0

        cards = None
        for line in lines_list:

            # Dealt should only be shown for hero!
            if "Dealt" in line:
                x = line.split()

                player_name = x[2].replace(" ", "")
                cards = [x[3].lstrip("["), x[4].rstrip("]")]

                if player_name not in data.keys():
                    data[player_name] = {}
                    if cards:
                        hero_cards_str = ""
                        for x in cards:
                            hero_cards_str += str(x) + " "
                        self._hero_cards = hero_cards_str.rstrip()
                        cards = None

            elif (
                    ":" in line
            ):  # I think having this filters out players joining table, disconnecting etc. for minor speed up

                if "Uncalled" in line:
                    player_name = line.split(" to ")[-1].strip()
                    if (play_phase == "Pre-Flop" and number_of_raises == 1) or (
                            play_phase != "Pre-Flop" and number_of_raises == 0):
                        if player_name not in data.keys():
                            data[player_name] = {}
                        data[player_name][f"{play_phase} Added to Pot"] = 0.0
                    else:
                        data[player_name][f"{play_phase} Added to Pot"] -= float(line.split()[2].strip("()$"))
                        pot -= float(line.split()[2].strip("()$"))
                    continue

                player_name = line.rsplit(":", 1)[0]

                if player_name not in data.keys():
                    data[player_name] = {}

                if f"{play_phase} Added to Pot" not in data[player_name].keys():
                    data[player_name][f"{play_phase} Added to Pot"] = 0.0

                action = line.rsplit(":")[1].rstrip()

                if (
                        play_phase == "Pre-Flop"
                        and f"{play_phase} Raise" not in data[player_name].keys()
                ):
                    if number_of_raises == 1:
                        data[player_name][f"Facing {play_phase} Raise"] = False
                    elif number_of_raises == 2:
                        data[player_name][f"Facing {play_phase} Raise"] = True
                    else:
                        data[player_name][f"Facing {play_phase} Raise"] = True
                        data[player_name][
                            f"Facing {play_phase} {number_of_raises}-Bet"
                        ] = True
                else:
                    if number_of_raises == 0:
                        data[player_name][f"Facing {play_phase} Raise"] = False
                    elif number_of_raises == 1:
                        data[player_name][f"Facing {play_phase} Raise"] = True
                    elif number_of_raises == 2:
                        data[player_name][f"Facing {play_phase} Re-Raise"] = True
                    else:
                        data[player_name][f"Facing {play_phase} Raise"] = True
                        data[player_name][
                            f"Facing {play_phase} {number_of_raises + 1}-Bet"
                        ] = True

                if all_in_raise:
                    data[player_name][f"Facing All In Raise"] = True

                if "bets" in action:

                    bet_data = action.split()

                    number_of_raises = 1
                    number_of_calls = 0

                    # player has raised (note this may be true for big blind)
                    data[player_name][play_phase + " Raise"] = True
                    data[player_name][play_phase + " Raise Size"] = bet_data[1].strip(
                        "$"
                    )
                    pot += float(bet_data[1].strip("$"))
                    data[player_name][f"{play_phase} Added to Pot"] += float(
                        bet_data[1].strip("$")
                    )

                    if "all-in" in action:
                        all_in_raise = True
                        data[player_name]["All In"] = True
                        data[player_name]["All In Street"] = play_phase
                        data[player_name]["All In Action"] = "Raise"

                elif "calls" in action:
                    call_data = action.split()
                    number_of_calls += 1

                    if all_in_raise:
                        data[player_name]["Call All In Raise"] = True
                    if play_phase == "Pre-Flop":
                        if player_name in data:
                            if (
                                    "Called " + play_phase + " Raise size"
                                    not in data[player_name]
                                    and play_phase + " Raise" not in data[player_name]
                            ):
                                if player_name == self._small_blind_player:
                                    data[player_name][
                                        f"{play_phase} Added to Pot"
                                    ] = float(self._small_blind)
                                    pot += float(self._small_blind)
                                if player_name == self._big_blind_player:
                                    data[player_name][
                                        f"{play_phase} Added to Pot"
                                    ] = float(self._big_blind)
                                    pot += float(self._big_blind)

                    # if player open limps
                    if number_of_raises == 1 and play_phase == "Pre-Flop":
                        data[player_name][play_phase + " Limp"] = True
                        pot += float(self._big_blind)

                    # else calling a bet
                    else:
                        if number_of_raises < 3:
                            data[player_name]["Called " + play_phase + " Raise"] = True
                            data[player_name][
                                "Called " + play_phase + " Raise size"
                                ] = call_data[1].strip("$")
                        else:
                            data[player_name][
                                "Called " + play_phase + f" {number_of_raises}-Bet"
                                ] = True
                            data[player_name][
                                "Called " + play_phase + f" {number_of_raises}-Bet Size"
                                ] = call_data[1].strip("$")
                    pot += float(call_data[1].strip("$"))

                    data[player_name][f"{play_phase} Added to Pot"] += float(
                        call_data[1].strip("$")
                    )

                    if "all-in" in action:
                        data[player_name]["All In"] = True
                        data[player_name]["All In Street"] = play_phase
                        data[player_name]["All In Action"] = "Call"

                elif "checks" in action:
                    data[player_name]["Check " + play_phase] = True

                elif "folds" in action:

                    if all_in_raise:
                        data[player_name]["Fold to All In Raise"] = True

                    if play_phase == "Pre-Flop":
                        if player_name == self._small_blind_player:
                            pot += float(self._small_blind)
                        if player_name == self._big_blind_player:
                            pot += float(self._big_blind)

                        if number_of_raises == 1:
                            data[player_name][f"Fold to {play_phase} Limp"] = True
                        elif number_of_raises == 1:
                            data[player_name][f"Fold to {play_phase} Raise"] = True
                        else:
                            data[player_name][
                                f"Fold to {play_phase} {number_of_raises}-Bet"
                            ] = True

                    else:
                        if number_of_raises == 1:
                            data[player_name][f"Fold to {play_phase} Raise"] = True
                        elif number_of_raises == 2:
                            data[player_name][f"Fold to {play_phase} Re-Raise"] = True
                        else:
                            data[player_name][
                                f"Fold to {play_phase} {number_of_raises + 1}-Bet"
                            ] = True

                elif "raises" in action:
                    number_of_raises += 1
                    raise_data = action.split()

                    if all_in_raise:
                        data[player_name][f"Raise Over All In Raise"] = True

                    if number_of_raises < 3:

                        if play_phase == "Pre-Flop":

                            # player has raised (note this may be true for big blind)
                            raise_type = "Raise"
                            data[player_name][play_phase + " Raise"] = True
                            data[player_name][play_phase + " Raise Size"] = raise_data[
                                1
                            ].strip("$")
                            data[player_name][play_phase + " Raise to"] = raise_data[
                                3
                            ].strip("$")

                            # get player position
                            general_data[
                                f"{play_phase} Raise Position"
                            ] = self.positions[player_name]
                        else:
                            raise_type = "Re-Raise"
                            # player has raised (note this may be true for big blind)
                            data[player_name][play_phase + " Re-raise"] = True
                            data[player_name][
                                play_phase + " Re-raise Size"
                                ] = raise_data[1].strip("$")
                            data[player_name][play_phase + " Re-raise to"] = raise_data[
                                3
                            ].strip("$")
                            data[player_name][
                                f"{play_phase} Re-Raise Position"
                            ] = self.positions[player_name]

                            # get player position
                            general_data[
                                f"{play_phase} Re-Raise Position"
                            ] = self.positions[player_name]

                    else:
                        # player has raised (note this may be true for big blind)
                        raise_type = f"{number_of_raises}-Bet"
                        data[player_name][
                            play_phase + f" {number_of_raises}-Bet"
                            ] = True
                        data[player_name][
                            play_phase + f" {number_of_raises}-Bet Size"
                            ] = raise_data[1].strip("$")
                        data[player_name][
                            play_phase + f" {number_of_raises}-Bet to"
                            ] = raise_data[3].strip("$")

                        # get player position
                        general_data[
                            f"{play_phase} {number_of_raises}-Bet Position"
                        ] = self.positions[player_name]

                    pot += float(raise_data[3].strip("$"))
                    data[player_name][f"{play_phase} Added to Pot"] += float(
                        raise_data[3].strip("$")
                    )

                    if "all-in" in action:
                        all_in_raise = True
                        data[player_name]["All In"] = True
                        data[player_name]["All In Street"] = play_phase
                        data[player_name]["All In Action"] = raise_type

        normalised_dict = dict([(k, pd.Series(v)) for k, v in data.items()])
        df = pd.DataFrame(normalised_dict).transpose()

        for key, value in general_data.items():
            df[key] = value

        df["Pot Increase " + play_phase] = pot

        # set all fill na needed
        nan_inplace_value_columns = [
            "Limp",
            "Raise",
            "Re-raise",
            "3-Bet",
            "4-Bet",
            "5-Bet",
        ]
        nan_inplace_value_columns = [
            f"{play_phase} " + x for x in nan_inplace_value_columns
        ]
        nan_inplace_value_columns += [f"Called {play_phase} Raise"]
        nan_inplace_value_columns += [f"Check {play_phase}"]

        for x in nan_inplace_value_columns:
            if x in df.columns:
                df[x].fillna(False, inplace=True)

        return df

    @staticmethod
    def operations(self, operator, line):
        return {
            "showed": re.findall("\[.*\]", line)[0],
        }.get(operator, None)

    def read_summary(self, lines_list):
        """
        A function that gets the summary information for a PokerStars game

        Args:
            lines_list (list):
                list of lines in the summary

        Returns:
            dataframe:
                DataFrame with players cards
            winners (list):
                list of winners
            winning_hands (list):
                list of winning hands
            winning_ranking (list):
                list of classification of winning hands
        """
        data = {}
        winners = []
        winning_hands = []
        winning_ranking = None
        for line in lines_list:
            if "showed" in line:
                a = re.sub("\(.*\)", "", line.split("showed")[0])
                name = re.sub("Seat [0-9]: ", "", a).strip()
                value = line.split("showed")[1].split("]")[0].lstrip(" [")
                data[name] = value

                if "won" in line:
                    if "showed" in line:
                        winning_hands.append(data[name])
                        winning_ranking = line.split("with")[1].strip(" \n")
                    winners.append(name)
            elif "mucked" in line:
                a = re.sub("\(.*\)", "", line.split("mucked")[0])
                b = re.sub("Seat [0-9]: ", "", a).strip()
                data[b] = line[-7:-2]
            elif "collected" in line:
                a = re.sub("\(.*\)", "", line.split("collected")[0])
                b = re.sub("Seat [0-9]: ", "", a).strip()
                winners.append(b)
            if "| Rake" in line:
                self.rake = float(line.split()[-1].lstrip("$"))
        if self.hero not in data.keys():
            data[self.hero] = str(self._hero_cards)

        return (
            pd.Series(list(data.values()), index=list(data.keys()), dtype="string"),
            winners,
            winning_hands,
            winning_ranking,
        )

    @staticmethod
    def get_final_table_cards(self, lines):
        for line in reversed(lines):
            if "Board [" in line:
                list_of_cards = re.findall("\[.+]", line)[0].strip("[]").split()
                return [Card(x) for x in list_of_cards]
        return None

    def read_pokerstars_file(self, lines: list, game_index=0):
        """
        A function that processes a pokerstars game and returns a dataframe with a summary of all events in game

        Args:
            lines (list):
                list of lines in a single PokerStars game
            game_index (int):
                index of game used to identify individual games in a collection

        Returns:

        """
        total_pot = 0.0

        # dictionary will later be converted to a pandas df
        data_dict = {}

        # process file
        game_text = self.split_game_to_events(file=None, lines=lines)

        # get table cards
        table_cards = self.get_final_table_cards(game_text["SUMMARY"], lines)

        # pre-deal data
        data_dict["General"] = self.read_pre_deal_lines(game_text["HEADER"])
        self.positions = data_dict["General"]["Seat Number"].map(self.seats)
        for key, value in self._search_dict.items():

            if value in game_text.keys():
                if game_text[value] and len(game_text[value]) > 1:
                    data_dict[key] = self.read_betting_action(
                        game_text[value], play_phase=key
                    )

        (
            data_dict["summary"],
            winners,
            winning_hands,
            winning_ranking,
        ) = self.read_summary(game_text["SUMMARY"])

        # get player card and table data
        data_dict["Card Information"] = self.get_card_information(
            data_dict["summary"], table_cards
        )

        # collect data
        events_df = data_dict
        for x in events_df.keys():
            events_df[x]["Player Name"] = list(events_df[x].index)
            # events_df[x].reset_index(inplace=True)

        events_df["General"]["Position"] = events_df["General"]["Seat Number"].map(self.seats)

        # Pre-Flop
        events_df["Pre-Flop"]["Pre-Flop Final Pot ($)"] = events_df["Pre-Flop"]["Pot Increase Pre-Flop"]

        events_df["Pre-Flop"]["Pre-Flop Final Pot (BB)"] = (
                events_df["Pre-Flop"]["Pre-Flop Final Pot ($)"] / events_df["General"]["Big Blind"]
        )

        events_df["General"]["Total Added to Pot"] = events_df["Pre-Flop"]["Pre-Flop Added to Pot"]
        events_df["General"]["Final Pot"] = events_df["Pre-Flop"]["Pre-Flop Final Pot ($)"]

        # Flop
        if "Flop" in data_dict.keys():
            events_df["Flop"]["Flop Final Pot ($)"] = (
                    events_df["Flop"]["Pot Increase Flop"] + events_df["Pre-Flop"]["Pre-Flop Final Pot ($)"]
            )
            events_df["Flop"]["Flop Final Pot (BB)"] = (
                    events_df["Flop"]["Flop Final Pot ($)"] / events_df["General"]["Big Blind"]
            )
            if not data_dict["Flop"].empty:
                events_df["General"]["Total Added to Pot"] += events_df["Flop"]["Flop Added to Pot"]

            events_df["General"]["Final Pot"] = events_df["Flop"]["Flop Final Pot ($)"]

            # Turn
        if "Turn" in data_dict.keys():
            events_df["Turn"]["Turn Final Pot ($)"] = (
                    events_df["Turn"]["Pot Increase Turn"] + events_df["Flop"]["Flop Final Pot ($)"]
            )
            events_df["Turn"]["Turn Final Pot (BB)"] = (
                    events_df["Turn"]["Turn Final Pot ($)"] / events_df["General"]["Big Blind"]
            )
            if not data_dict["Turn"].empty:
                events_df["General"]["Total Added to Pot"] += events_df["Turn"]["Turn Added to Pot"]

            events_df["General"]["Final Pot"] = events_df["Turn"]["Turn Final Pot ($)"]

        # River
        if "River" in data_dict.keys():
            events_df["River"]["River Final Pot ($)"] = (
                    events_df["River"]["Pot Increase River"] + events_df["Turn"]["Turn Final Pot ($)"]
            )
            events_df["River"]["River Final Pot (BB)"] = (
                    events_df["River"]["River Final Pot ($)"] / events_df["General"]["Big Blind"]
            )
            if not data_dict["River"].empty:
                events_df["General"]["Total Added to Pot"] += events_df["River"]["River Added to Pot"]

            events_df["General"]["Final Pot"] = events_df["River"]["River Final Pot ($)"]

        data_dict["General"]["Is Winner"] = np.where(data_dict["General"]["Player Name"].isin(winners),
                                                     True,
                                                     False)
        data_dict["General"]["Player Profit"] = np.where(data_dict["General"]["Is Winner"],
                                                         data_dict["General"]["Final Pot"] - self.rake,
                                                         -data_dict["General"]["Total Added to Pot"])

        game = PokerStarsGame(
            [item for sublist in game_text.values() for item in sublist],
            events_df,
            table_cards,
            winners=winners,
            winning_hands=winning_hands,
            winning_ranking=winning_ranking,
            game_index=game_index,
        )
        return game

    @staticmethod
    def get_card_information(player_cards: pd.Series, table_cards: list):
        """
        A function that, given a series of players cards and the community table cards, will return a dataframe of all
        the relevant  draws, rankings and combos

        Args:
            player_cards (Series):
                DataFrame of cards each player has. A player is ignored if hand not specified
            table_cards (list):
                List of community table cards

        Returns:
            card_information_data (DataFrame):
                DataFrame of all relevant card ranking information

        """
        data = {x: {} for x in player_cards.index}

        for player, hand in player_cards.items():
            data[player]["Player Card 1"] = hand[0:2]
            data[player]["Player Card 2"] = hand[3:5]
            new_hand = [Card(hand[0:2]), Card(hand[3:5])]
            if hand[0] == hand[3]:
                data[player]["Pocket Pair"] = True
            else:
                data[player]["Pocket Pair"] = False

            if hand[1] == hand[4]:
                data[player]["Suited Hand"] = True
            else:
                data[player]["Suited Hand"] = False

            player_data = SingleBoardAnalysis(new_hand, table_cards).data_analysis
            data[player].update(player_data)

            # check if cards in players hand are in the best combination of cards
            data[player]["Number of Best Cards in Hand"] = 0
            if data[player]["Best Cards"] is not None:
                if data[player]["Player Card 1"] in data[player]["Best Cards"]:
                    data[player]["Number of Best Cards in Hand"] += 1
                if data[player]["Player Card 2"] in data[player]["Best Cards"]:
                    data[player]["Number of Best Cards in Hand"] += 1

        df = pd.DataFrame(data).transpose()
        return df

    def winning_games(self, winner=None):
        """

        Args:
            player: str
                Name of winning player
        Returns:
            winner_dict

        """
        if not winner:
            winner = self.player
        return {
            game.game_index: game
            for game in self.games_data.values()
            if winner in game.winners
        }

    def save_to_csv_files(self, file_root):
        """
        A function to save all dataframes to csv files ready for reading
        Args:
            file_root:

        Returns:

        """

    def save_data(self, save_file):
        import pyarrow as pa
        import pyarrow.parquet as pq
        import os

        if os.path.isfile(save_file):
            print(f"Database exists!")
            data = pq.read_table(save_file).to_pandas()
            save_data = (
                pd.concat([data, self.full_data])
                .drop_duplicates()
                .reset_index(drop=True)
            )
            table = pa.Table.from_pandas(save_data)
            pq.write_table(table, save_file)
        else:
            table_general = pa.Table.from_pandas(self.full_data["General"])
            table_pre_flop = pa.Table.from_pandas(self.full_data["Pre-Flop"])
            table_flop = pa.Table.from_pandas(self.full_data["Flop"])
            table_turn = pa.Table.from_pandas(self.full_data["Turn"])
            table_river = pa.Table.from_pandas(self.full_data["River"])
            table_cards = pa.Table.from_pandas(self.full_data["Card Information"])

            pq.write_table(table_general, save_file + "_general.parquet")
            pq.write_table(table_pre_flop, save_file + "_pre-flop.parquet")
            pq.write_table(table_flop, save_file + "_flop.parquet")
            pq.write_table(table_turn, save_file + "_turn.parquet")
            pq.write_table(table_river, save_file + "_river.parquet")
            pq.write_table(table_cards, save_file + "_card_info.parquet")
