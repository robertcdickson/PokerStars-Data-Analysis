import copy
import itertools
import random
import re
import sys

import pandas
import pandas as pd
from collections import Counter
from src.poker_main import *
import pyarrow


class PokerStarsGame(object):
    """
    An object containing all datat related to a game player on Pokerstars.
    """

    def __init__(
            self,
            game_text,
            data,
            table_cards,
            winners,
            winning_hands,
            hero="bobsondugnutt11",
            game_index=0,
            hero_cards=None,
    ):
        """

        Args:
            game_text: (str)
                The whole text read out from the pokerstars output file
            data (Dataframe):
                A dataframe with different attributes of the game
            table_cards (str):
                String of cards on table
            winners (list):
                List of the winners of the game
            winning_hands (list):
                List of hands that won the game
            hero: (str)
                Name of player defined as hero
            game_index (int):
                An index used to track PokerStarsCollection games
            hero_cards: (list)
                A list of hero's cards

        """
        self.suits = {"c": "clubs", "s": "spades", "d": "diamonds", "h": "hearts"}

        self.values = {
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

        self.deck = [Card(value + suit) for suit in self.suits for value in self.values]
        if data is None:
            self.data = self.get_data_from_text()

        self.data = data
        self.game_index = game_index
        self.game_text = game_text
        self.winners = winners
        self.winning_hands = winning_hands
        self.hero = hero
        self.hero_cards = hero_cards

        self.flop_cards = None
        self.turn_card = None
        self.river_card = None

        if table_cards:
            self.table_cards = table_cards
            if len(table_cards) >= 3:
                self.flop_cards = table_cards[0:3]
            if len(table_cards) >= 4:
                self.turn_card = table_cards[3]
            if len(table_cards) == 5:
                self.river_card = table_cards[4]
        else:
            self.table_cards = None

        self.big_blind = self.get_blind("BB")
        self.small_blind = self.get_blind("SB")
        self.chip_leader = self.data.index[
            self.data["Chips ($)"] == self.data["Chips ($)"].max()
            ].to_list()

        self.player_cards_text = self.get_player_cards()

        self.player_names = None
        self.player_final_action = None

        self.final_pot = self.get_final_pot()

        self.all_column_labels = [
            # General Data
            "Player Name",
            "Stakes",
            "Max Players",
            "Game Type",
            "Date",
            "Time",
            "Game Code",
            "Table Name",
            "Chips ($)",
            "Chips (BB)",
            "Player Cards",
            "Position",
            # pre-flop
            "Check Pre-Flop",
            "Pre-Flop Limp",
            "Pre-Flop Raise",
            "Pre-Flop Raise Size",
            "Pre-Flop Raise to",
            "Called Pre-Flop Raise",
            "Called Pre-Flop Raise size",
            "Fold to Pre-Flop Raise",
            "Pre-Flop 3-Bet",
            "Pre-Flop 3-Bet Size",
            "Pre-Flop 3-Bet to",
            "Called Pre-Flop 3-Bet",
            "Called Pre-Flop 3-Bet Size",
            "Fold to Pre-Flop 3-Bet",
            "Pre-Flop 4-Bet",
            "Pre-Flop 4-Bet Size",
            "Pre-Flop 4-Bet to",
            "Called Pre-Flop 4-Bet",
            "Called Pre-Flop 4-Bet Size",
            "Fold to Pre-Flop 4-Bet",
            "Pre-Flop 5-Bet",
            "Pre-Flop 5-Bet Size",
            "Pre-Flop 5-Bet to",
            "Called Pre-Flop 5-Bet",
            "Called Pre-Flop 5-Bet Size",
            "Fold to Pre-Flop 5-Bet",
            "Pre-Flop 6-Bet",
            "Pre-Flop 6-Bet Size",
            "Pre-Flop 6-Bet to",
            "Called Pre-Flop 6-Bet",
            "Called Pre-Flop 6-Bet Size",
            "Fold to Pre-Flop 6-Bet",
            # flop
            "Check Flop",
            "Flop Raise",
            "Flop Raise Size",
            "Flop Raise to",
            "Called Flop Raise",
            "Called Flop Raise size",
            "Fold to Flop Raise",
            "Flop Re-raise",
            "Flop Re-raise Size",
            "Flop Re-raise to",
            "Called Flop Re-raise",
            "Called Flop Re-raise Size",
            "Fold to Flop Re-raise",
            "Flop 3-Bet",
            "Flop 3-Bet Size",
            "Flop 3-Bet to",
            "Called Flop 3-Bet",
            "Called Flop 3-Bet Size",
            "Fold to Flop 3-Bet",
            "Flop 4-Bet",
            "Flop 4-Bet Size",
            "Flop 4-Bet to",
            "Called Flop 4-Bet",
            "Called Flop 4-Bet Size",
            "Fold to Flop 4-Bet",
            "Flop 5-Bet",
            "Flop 5-Bet Size",
            "Flop 5-Bet to",
            "Called Flop 5-Bet",
            "Called Flop 5-Bet Size",
            "Fold to Flop 5-Bet",
            "Flop 6-Bet",
            "Flop 6-Bet Size",
            "Flop 6-Bet to",
            "Called Flop 6-Bet",
            "Called Flop 6-Bet Size",
            "Fold to Flop 6-Bet",
            # Turn
            "Check Turn",
            "Turn Raise",
            "Turn Raise Size",
            "Turn Raise to",
            "Called Turn Raise",
            "Called Turn Raise size",
            "Fold to Turn Raise",
            "Turn Re-raise",
            "Turn Re-raise Size",
            "Turn Re-raise to",
            "Called Turn Re-raise",
            "Called Turn Re-raise Size",
            "Fold to Turn Re-raise",
            "Turn 3-Bet",
            "Turn 3-Bet Size",
            "Turn 3-Bet to",
            "Called Turn 3-Bet",
            "Called Turn 3-Bet Size",
            "Fold to Turn 3-Bet",
            "Turn 4-Bet",
            "Turn 4-Bet Size",
            "Turn 4-Bet to",
            "Called Turn 4-Bet",
            "Called Turn 4-Bet Size",
            "Fold to Turn 4-Bet",
            "Turn 5-Bet",
            "Turn 5-Bet Size",
            "Turn 5-Bet to",
            "Called Turn 5-Bet",
            "Called Turn 5-Bet Size",
            "Fold to Turn 5-Bet",
            "Turn 6-Bet",
            "Turn 6-Bet Size",
            "Turn 6-Bet to",
            "Called Turn 6-Bet",
            "Called Turn 6-Bet Size",
            "Fold to Turn 6-Bet",
            # River
            "Check River",
            "River Raise",
            "River Raise Size",
            "River Raise to",
            "Called River Raise",
            "Called River Raise size",
            "Fold to River Raise",
            "River Re-raise",
            "River Re-raise Size",
            "River Re-raise to",
            "Called River Re-raise",
            "Called River Re-raise Size",
            "Fold to River Re-raise",
            "River 3-Bet",
            "River 3-Bet Size",
            "River 3-Bet to",
            "Called River 3-Bet",
            "Called River 3-Bet Size",
            "Fold to River 3-Bet",
            "River 4-Bet",
            "River 4-Bet Size",
            "River 4-Bet to",
            "Called River 4-Bet",
            "Called River 4-Bet Size",
            "Fold to River 4-Bet",
            "River 5-Bet",
            "River 5-Bet Size",
            "River 5-Bet to",
            "Called River 5-Bet",
            "Called River 5-Bet Size",
            "Fold to River 5-Bet",
            "River 6-Bet",
            "River 6-Bet Size",
            "River 6-Bet to",
            "Called River 6-Bet",
            "Called River 6-Bet Size",
            "Fold to River 6-Bet",
        ]

        if "Zoom" in self.game_text[0]:
            self.game_type = "Zoom"
            self.game_code = self.game_text[0].split("#")[1].split(":")[0]
            self.stakes = self.game_text[0].split("(")[1].split(")")[0]
            self.big_blind_size = float(self.stakes.split("/")[1].strip("$"))
            self.data["Chips (BB)"] = self.data["Chips ($)"] / self.big_blind_size
            self.date = self.game_text[0].split("-")[1].split("[")[0].split(" ")[1]
            self.time = self.game_text[0].split("-")[1].split("[")[0].split(" ")[2]
            self.max_players = self.game_text[1].split("'")[2].split(" ")[1]
            self.table_name = self.game_text[1].split("'")[1]
        else:
            self.game_type = "Normal"
            self.game_code = self.game_text[0].split("#")[1].split(":")[0]
            self.stakes = self.game_text[0].split("(")[1].split(")")[0].split(" ")[0]
            self.big_blind_size = float(self.stakes.split("/")[1].strip("$").split()[0])
            self.data["Chips (BB)"] = self.data["Chips ($)"] / self.big_blind_size
            self.date = self.game_text[0].split("-")[1].split("[")[0].split(" ")[1]
            self.time = self.game_text[0].split("-")[1].split("[")[0].split(" ")[2]
            self.max_players = self.game_text[1].split("'")[2].split(" ")[1]
            self.table_name = self.game_text[1].split("'")[1]

        self.values_for_full_data = {
            "Game Type": self.game_type,
            "Game Code": self.game_code,
            "Stakes": self.stakes,
            "Date": self.date,
            "Time": self.time,
            "Max Players": self.max_players,
            "Table Name": self.table_name,
        }

    def reorder_columns(self, df):
        new_column_labels = [
            x for x in self.all_column_labels if x in df.columns
        ]
        return df[new_column_labels]

    def get_blind(self, size: str):
        """
        Function to get blinds

        Args:
            size (str):
                Describes blind type. Options: "BB" or "SB"

        Returns:

        """
        return self.data.index[self.data["Position"] == size].to_list()

    def translate_hand(self, hand):
        # translates hand from pokerstars output format to list of tuples
        return [(int(self.values[card[0]]), self.suits[card[1]]) for card in hand]

    def get_player_cards(self):
        for line in self.game_text:
            if "Dealt" in line and self.hero in line:
                cards = line.split("[")[-1].rstrip("]\n").split()
                return [Card(x) for x in cards]

    def get_final_pot(self):
        for line in self.game_text:
            if "collected" in line:
                return float(line.split("$")[-1].split()[0].strip("()"))

    def get_data_from_text(self):
        pass

    def get_full_data(self):
        new_df = self.data
        for key, value in self.values_for_full_data.items():
            new_df[key] = value
        self.reorder_columns(new_df)
        return new_df

    def simulate_game(
            self, players=None, n=100, use_table_cards=True, table_card_length=5
    ):
        """
        A function that runs a simulation for n poker_session to see how likely a hero is to win pre flop against
        other hands
        Args:
            players:
            n_table_cards:
            specified_table_cards:
            n:

        Returns:

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
            file,
            working_dir,
            encoding="ISO-8859-14",
            hero="Bobson_Dugnutt",
            write_files=False,
            max_games=None
    ):

        self.suits = {"c": "clubs", "s": "spades", "d": "diamonds", "h": "hearts"}

        self.values = {
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
        self.hero_cards = None
        self.search_dict = {
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

        self.encoding = encoding
        self.games_text = self.process_file(split_files=write_files)
        self.games_data = {}

        self.all_column_labels = [
            # General Data
            "Player Name",
            "Stakes",
            "Max Players",
            "Game Type",
            "Date",
            "Time",
            "Game Code",
            "Table Name",
            "Chips ($)",
            "Chips (BB)",
            "Player Cards",
            "Position",
            # pre-flop
            "Check Pre-Flop",
            "Pre-Flop Limp",
            "Pre-Flop Raise",
            "Pre-Flop Raise Size",
            "Pre-Flop Raise to",
            "Called Pre-Flop Raise",
            "Called Pre-Flop Raise size",
            "Fold to Pre-Flop Raise",
            "Pre-Flop 3-Bet",
            "Pre-Flop 3-Bet Size",
            "Pre-Flop 3-Bet to",
            "Called Pre-Flop 3-Bet",
            "Called Pre-Flop 3-Bet Size",
            "Fold to Pre-Flop 3-Bet",
            "Pre-Flop 4-Bet",
            "Pre-Flop 4-Bet Size",
            "Pre-Flop 4-Bet to",
            "Called Pre-Flop 4-Bet",
            "Called Pre-Flop 4-Bet Size",
            "Fold to Pre-Flop 4-Bet",
            "Pre-Flop 5-Bet",
            "Pre-Flop 5-Bet Size",
            "Pre-Flop 5-Bet to",
            "Called Pre-Flop 5-Bet",
            "Called Pre-Flop 5-Bet Size",
            "Fold to Pre-Flop 5-Bet",
            "Pre-Flop 6-Bet",
            "Pre-Flop 6-Bet Size",
            "Pre-Flop 6-Bet to",
            "Called Pre-Flop 6-Bet",
            "Called Pre-Flop 6-Bet Size",
            "Fold to Pre-Flop 6-Bet",
            # flop
            "Check Flop",
            "Flop Raise",
            "Flop Raise Size",
            "Flop Raise to",
            "Called Flop Raise",
            "Called Flop Raise size",
            "Fold to Flop Raise",
            "Flop Re-raise",
            "Flop Re-raise Size",
            "Flop Re-raise to",
            "Called Flop Re-raise",
            "Called Flop Re-raise Size",
            "Fold to Flop Re-raise",
            "Flop 3-Bet",
            "Flop 3-Bet Size",
            "Flop 3-Bet to",
            "Called Flop 3-Bet",
            "Called Flop 3-Bet Size",
            "Fold to Flop 3-Bet",
            "Flop 4-Bet",
            "Flop 4-Bet Size",
            "Flop 4-Bet to",
            "Called Flop 4-Bet",
            "Called Flop 4-Bet Size",
            "Fold to Flop 4-Bet",
            "Flop 5-Bet",
            "Flop 5-Bet Size",
            "Flop 5-Bet to",
            "Called Flop 5-Bet",
            "Called Flop 5-Bet Size",
            "Fold to Flop 5-Bet",
            "Flop 6-Bet",
            "Flop 6-Bet Size",
            "Flop 6-Bet to",
            "Called Flop 6-Bet",
            "Called Flop 6-Bet Size",
            "Fold to Flop 6-Bet",
            # Turn
            "Check Turn",
            "Turn Raise",
            "Turn Raise Size",
            "Turn Raise to",
            "Called Turn Raise",
            "Called Turn Raise size",
            "Fold to Turn Raise",
            "Turn Re-raise",
            "Turn Re-raise Size",
            "Turn Re-raise to",
            "Called Turn Re-raise",
            "Called Turn Re-raise Size",
            "Fold to Turn Re-raise",
            "Turn 3-Bet",
            "Turn 3-Bet Size",
            "Turn 3-Bet to",
            "Called Turn 3-Bet",
            "Called Turn 3-Bet Size",
            "Fold to Turn 3-Bet",
            "Turn 4-Bet",
            "Turn 4-Bet Size",
            "Turn 4-Bet to",
            "Called Turn 4-Bet",
            "Called Turn 4-Bet Size",
            "Fold to Turn 4-Bet",
            "Turn 5-Bet",
            "Turn 5-Bet Size",
            "Turn 5-Bet to",
            "Called Turn 5-Bet",
            "Called Turn 5-Bet Size",
            "Fold to Turn 5-Bet",
            "Turn 6-Bet",
            "Turn 6-Bet Size",
            "Turn 6-Bet to",
            "Called Turn 6-Bet",
            "Called Turn 6-Bet Size",
            "Fold to Turn 6-Bet",
            # River
            "Check River",
            "River Raise",
            "River Raise Size",
            "River Raise to",
            "Called River Raise",
            "Called River Raise size",
            "Fold to River Raise",
            "River Re-raise",
            "River Re-raise Size",
            "River Re-raise to",
            "Called River Re-raise",
            "Called River Re-raise Size",
            "Fold to River Re-raise",
            "River 3-Bet",
            "River 3-Bet Size",
            "River 3-Bet to",
            "Called River 3-Bet",
            "Called River 3-Bet Size",
            "Fold to River 3-Bet",
            "River 4-Bet",
            "River 4-Bet Size",
            "River 4-Bet to",
            "Called River 4-Bet",
            "Called River 4-Bet Size",
            "Fold to River 4-Bet",
            "River 5-Bet",
            "River 5-Bet Size",
            "River 5-Bet to",
            "Called River 5-Bet",
            "Called River 5-Bet Size",
            "Fold to River 5-Bet",
            "River 6-Bet",
            "River 6-Bet Size",
            "River 6-Bet to",
            "Called River 6-Bet",
            "Called River 6-Bet Size",
            "Fold to River 6-Bet",
        ]

        i = 0
        for key, game in self.games_text.items():
            if self.max_games and i >= self.max_games:
                break
            self.games_data[key] = self.read_pokerstars_file(lines=game, game_index=i)
            i += 1

        self.winners = [game.winners[0] for game in self.games_data.values()]
        self.winner_count = Counter(self.winners)

        self.full_data = pd.concat(
            [x.get_full_data() for x in self.games_data.values()]
        )
        self.full_data = self.full_data.reset_index(drop=True)
        self.full_data = self.reorder_columns()

    def process_file(self, split_files=False):

        # a function that chunks a file of poker stars hands into individual poker_session
        files_dict = {}
        file_number = 0

        # open file with pokerstars data in it
        with open(self.file, "r", encoding=self.encoding) as rf:

            line_marker = 0

            # start and write markers need for starting/stopping of file chunk
            start = False
            write = False

            for line in rf.readlines():
                if (
                        "PokerStarsCollection Hand" in line
                        or "PokerStars Zoom Hand" in line
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
    def read_hand(hand, hand_regex):
        # reads in a hand given a hand regex
        return hand_regex.findall(hand)[0].strip("[]").split()

    def reorder_columns(self):
        new_column_labels = [
            x for x in self.all_column_labels if x in self.full_data.columns.to_list()
        ]
        return self.full_data[new_column_labels]

    def translate_hand(self, hand):
        # translates hand from pokerstars output format to list of tuples
        return [(self.values[card[0]], self.suits[card[1]]) for card in hand]

    def read_hand_file(self, file):
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

    def get_button_seat(self, file):
        # returns the index of the seat currently on the button
        with open(file, "r") as rf:
            return int(re.search("#\d", rf.readlines()[1]).group().strip("#"))

    def split_game_to_events(self, file, lines):
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

        data_dict = {"Player Name": [], "Seat Number": [], "Chips ($)": []}

        button_seat = int(re.search("#\d", player_list[1]).group().strip("#"))

        for line in player_list:
            player = re.findall(":.*\(", line)
            if player and "chips" in line:
                # get hero name and number of chips
                line_list = line.split(" ")

                # get different pieces of data pre dealing
                seat_number = int(line_list[1].strip(":"))
                player_name = re.sub("[:\( ]", "", player[0])
                chips = float(line_list[-4].strip("($"))  # THIS MAY BE A PROBLEM TEST

                data_dict["Player Name"].append(player_name)
                data_dict["Seat Number"].append(seat_number)
                data_dict["Chips ($)"].append(chips)

        # renumber seat numbers for ordering of play
        new_seat_order = [i for i in range(1, len(data_dict["Seat Number"]) + 1)]
        data_dict["Play Order"] = []
        new_button = new_seat_order[data_dict["Seat Number"].index(button_seat)]

        data_dict["Play Order"] = [seat - new_button + len(data_dict["Seat Number"]) if int(seat) - new_button < 0
                                   else seat - new_button if int(seat) - new_button > 0
        else len(data_dict["Seat Number"]) for seat in new_seat_order]

        """for seat in new_seat_order:
            if int(seat) - new_button < 0:
                data_dict["Play Order"].append(
                    seat - new_button + len(data_dict["Seat Number"])
                )
            elif int(seat) - new_button > 0:
                data_dict["Play Order"].append(seat - new_button)
            else:
                data_dict["Play Order"].append(len(data_dict["Seat Number"]))"""

        data_dict["Betting Order"] = [
            i - 2 if i - 2 > 0 else i - 2 + len(data_dict["Play Order"])
            for i in data_dict["Play Order"]
        ]
        data_dict["Big Blind"] = [
            True if j == 2 else False for j in data_dict["Play Order"]
        ]
        data_dict["Small Blind"] = [
            True if j == 1 else False for j in data_dict["Play Order"]
        ]

        data_df = pd.DataFrame(data_dict).set_index(["Player Name"])
        return data_df

    def read_betting_action(self, lines_list, play_phase=None):
        data = {}

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
                        self.hero_cards = hero_cards_str.rstrip()
                        cards = None

            elif (
                    ":" in line
            ):  # I think having this filters out players joining table, disconnecting etc. for speed up
                player_name = line.split(":")[0].replace(" ", "")

                if player_name not in data.keys():
                    data[player_name] = {}

                action = line.split(":")[1].rstrip()

                if "bets" in action:

                    bet_data = action.split()

                    number_of_raises = 1
                    number_of_calls = 0

                    # player has raised (note this may be true for big blind)
                    data[player_name][play_phase + " Raise"] = True
                    data[player_name][play_phase + " Raise Size"] = bet_data[1].strip(
                        "$"
                    )

                elif "calls" in action:
                    call_data = action.split()
                    number_of_calls += 1

                    # if player open limps
                    if number_of_raises == 1 and play_phase == "Pre-flop":
                        data[player_name][play_phase + " Limp"] = True

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
                elif "checks" in action:
                    data[player_name]["Check " + play_phase] = True

                elif "folds" in action:
                    if number_of_raises == 1 and play_phase == "Pre-flop":
                        data[player_name]["Fold to " + play_phase + " Limp"] = True
                    else:
                        data[player_name]["Fold to " + play_phase + " Raise"] = True

                elif "raises" in action:
                    number_of_raises += 1
                    raise_data = action.split()
                    if number_of_raises < 3:
                        if play_phase == "Pre-Flop":
                            # player has raised (note this may be true for big blind)
                            data[player_name][play_phase + " Raise"] = True
                            data[player_name][play_phase + " Raise Size"] = raise_data[
                                1
                            ].strip("$")
                            data[player_name][play_phase + " Raise to"] = raise_data[
                                3
                            ].strip("$")
                        else:
                            # player has raised (note this may be true for big blind)
                            data[player_name][play_phase + " Re-raise"] = True
                            data[player_name][
                                play_phase + " Re-raise Size"
                                ] = raise_data[1].strip("$")
                            data[player_name][play_phase + " Re-raise to"] = raise_data[
                                3
                            ].strip("$")
                    else:
                        # player has raised (note this may be true for big blind)
                        data[player_name][
                            play_phase + f" {number_of_raises}-Bet"
                            ] = True
                        data[player_name][
                            play_phase + f" {number_of_raises}-Bet Size"
                            ] = raise_data[1].strip("$")
                        data[player_name][
                            play_phase + f" {number_of_raises}-Bet to"
                            ] = raise_data[3].strip("$")

        normalised_dict = dict([(k, pd.Series(v)) for k, v in data.items()])
        df = pd.DataFrame(normalised_dict).transpose()

        # set all fill na needed
        nan_inplace_value_columns = ["Raise", "Re-raise", "3-Bet", "4-Bet", "5-Bet"]
        nan_inplace_value_columns = [
            f"{play_phase} " + x for x in nan_inplace_value_columns
        ]
        nan_inplace_value_columns += [f"Called {play_phase} Raise"]
        nan_inplace_value_columns += [f"Check {play_phase}"]

        for x in nan_inplace_value_columns:
            if x in df.columns:
                df[x].fillna(False, inplace=True)
        # df["pre-flop 5-bet"].fillna(False, inplace=True)
        # df.columns = [f"{play_phase.capitalize()} Action {i}" for i in range(1, len(df.columns) + 1)]

        return df

    def operations(self, operator, line):
        return {
            "showed": re.findall("\[.*\]", line)[0],
        }.get(operator, None)

    def read_summary(self, lines_list):
        data = {}
        winners = []
        winning_hands = []
        for line in lines_list:
            if "showed" in line:
                a = re.sub("\(.*\)", "", line.split("showed")[0])
                b = re.sub("Seat [0-9]: ", "", a).strip()
                data[b] = re.findall("\[.+]", line)[0].strip("[]")
                if "won" in line:
                    if "showed" in line:
                        winning_hands.append(data[b])
                    winners.append(b)
            elif "mucked" in line:
                a = re.sub("\(.*\)", "", line.split("mucked")[0])
                b = re.sub("Seat [0-9]: ", "", a).strip()
                data[b] = re.findall("\[.+]", line)[0].strip("[]")
            elif "collected" in line:
                a = re.sub("\(.*\)", "", line.split("collected")[0])
                b = re.sub("Seat [0-9]: ", "", a).strip()
                winners.append(b)

        if self.hero not in data.keys():
            data[self.hero] = str(self.hero_cards)

        return (
            pd.DataFrame(data.values(), index=data.keys(), columns=["Player Cards"]),
            winners,
            winning_hands,
        )

    @staticmethod
    def get_final_table_cards(self, lines):
        for line in reversed(lines):
            if "Board [" in line:
                list_of_cards = re.findall("\[.+]", line)[0].strip("[]").split()
                return [Card(x) for x in list_of_cards]
        return None

    def read_pokerstars_file(self, lines, game_index=0):
        """
        A function that processes a pokerstars game and returns a dataframe with a summary of all events in game

        Args:
            lines:
            file (str): file to read

        Returns:
            events df (pandas df)
        """

        # dictionary will later be converted to a pandas df
        data_dict = {}

        # process file
        game_text = self.split_game_to_events(file=None, lines=lines)

        # get table cards
        table_cards = self.get_final_table_cards(game_text["SUMMARY"], lines)

        # pre-deal data
        data_dict["pre_action"] = self.read_pre_deal_lines(game_text["HEADER"])

        for key, value in self.search_dict.items():
            try:
                data_dict[key] = self.read_betting_action(
                    game_text[value], play_phase=key
                )
            except KeyError:
                break

        data_dict["summary"], winners, winning_hands = self.read_summary(
            game_text["SUMMARY"]
        )

        events_df = pd.concat([val for val in data_dict.values()], axis=1)
        events_df["Player Name"] = list(events_df.index)
        events_df.reset_index(inplace=True)
        events_df["Position"] = events_df["Seat Number"].map(self.seats)

        # these columns seem a bit useless so adding this as a temporary
        events_df = events_df.drop(
            [
                "index",
                "Seat Number",
                "Play Order",
                "Betting Order",
                "Big Blind",
                "Small Blind",
            ],
            axis=1,
        )

        game = PokerStarsGame(
            [item for sublist in game_text.values() for item in sublist],
            events_df,
            table_cards,
            winners=winners,
            winning_hands=winning_hands,
            game_index=game_index,
        )
        return game

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

    def save_data(self, save_file):
        import pyarrow as pa
        import pyarrow.parquet as pq
        import os
        if os.path.isfile(save_file):
            print(f"Database exists!")
            data = pq.read_table(save_file).to_pandas()
            save_data = pd.concat([data, self.full_data]).drop_duplicates().reset_index(drop=True)
            table = pa.Table.from_pandas(save_data)
            pq.write_table(table, save_file)
        else:
            table = pa.Table.from_pandas(self.full_data)
            pq.write_table(table, save_file)
