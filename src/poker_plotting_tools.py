
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_hand_matrix(hand_counts, translate=True):
    # uses df counts to plot a heatmap in a hand matrix

    list_of_rankings = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
    data_counter = {a: {b: 0 for b in list_of_rankings} for a in list_of_rankings}
    for x, y in zip(list(hand_counts.index), hand_counts):
        if translate:
            x = x.replace(" ", "")

            if list_of_rankings.index(x[0]) > list_of_rankings.index(x[2]):
                if x[0] == x[2]:
                    counter_key = x[0] + x[2]
                elif x[1] == x[3]:
                    counter_key = x[0] + x[2]
                else:
                    counter_key = x[2] + x[0]
            else:
                if x[0] == x[2]:
                    counter_key = x[0] + x[2]
                elif x[1] == x[3]:
                    counter_key = x[2] + x[0]
                else:
                    counter_key = x[0] + x[2]

            data_counter[counter_key[0]][counter_key[1]] += y
        else:
            data_counter[x[0]][x[1]] += y

    heatmap_data = pd.DataFrame.from_dict(data_counter).fillna(0)
    plt.figure(figsize=(12, 9))
    all_ranking_combos = []
    for a in list_of_rankings:
        row = []
        for y in list_of_rankings:
            # suited
            if list_of_rankings.index(a) < list_of_rankings.index(y):
                row.append(a + y + "s")
            # unsuited
            elif list_of_rankings.index(a) > list_of_rankings.index(y):
                row.append(y + a + "o")
            # pairs
            else:
                row.append(a + y)

        all_ranking_combos.append(row)

    rankings = pd.DataFrame(all_ranking_combos)
    hm = sns.heatmap(heatmap_data,
                     cmap=plt.cm.get_cmap("hot"),
                     annot=all_ranking_combos,
                     fmt = '',
                     xticklabels=False,
                     yticklabels=False,
                     cbar=True,
                     linewidths=2.5,
                     linecolor = (0, 0, 0),
                     annot_kws={"fontsize": 20}, square=True)

    cbar = hm.collections[0].colorbar
    cbar.ax.tick_params(labelsize=20)
    for _, spine in hm.spines.items():
        spine.set_visible(True)
        spine.set_linewidth(2.5)
        spine.set_color("black")
    plt.tight_layout()

def encode_hand(hand):
    rankings = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
    if hand is None:
        return None
    hand = hand.replace(" ", "")
    if len(hand) != 4:
        return None
    if rankings.index(hand[0]) > rankings.index(hand[2]):
        if hand[0] == hand[2]:
            new_hand = hand[0] + hand[2]
        elif hand[1] == hand[3]:
            new_hand = hand[0] + hand[2]
        else:
            new_hand = hand[2] + hand[0]
    else:
        if hand[0] == hand[2]:
            new_hand = hand[0] + hand[2]
        elif hand[1] == hand[3]:
            new_hand = hand[2] + hand[0]
        else:
            new_hand = hand[0] + hand[2]
    return new_hand