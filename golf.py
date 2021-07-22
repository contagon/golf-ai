from terminal_playing_cards import View, Deck, Card 
from terminal_playing_cards.config import DEFAULT_DECK_SPEC
from terminal_playing_cards.utils import convert_layers_to_string   
import os
from numpy.random import randint
import numpy as np

class Golf:
    def __init__(self, n_players=2):
        self.n_players = n_players
        self.turn = 0
        self.ender = None
        self.drawn = None

        # Set up deck
        specs = dict(DEFAULT_DECK_SPEC)
        specs.update({ 'K': {'clubs': 0, 'diamonds': 0, 'spades': 0, 'hearts': 0},
                        '2': {'clubs': -2, 'diamonds': -2, 'spades': -2, 'hearts': -2},
                        'J': {'clubs': 10, 'diamonds': 10, 'spades': 10, 'hearts': 10},
                        'Q': {'clubs': 10, 'diamonds': 10, 'spades': 10, 'hearts': 10}})
        
        self.deck = Deck(specifications=specs, hidden=True, picture=False)
        self.deck.shuffle()

        # setup piles
        self.discard = []
        self.hands = [[self.deck.pop() for _ in range(6)] for _ in range(self.n_players)]
        for h in self.hands:
            h[0].hidden = False
            h[1].hidden = False

    def draw(self, player, pile):
        if(player != self.turn):
            print("Wrong player is going!")
            return None

        if pile in [0, "0", "draw"]:
            self.drawn = self.deck.pop()
            self.drawn.hidden = False
        
        elif pile in [1, "1", "discard"]:
            if len(self.discard) == 0:
                print("Can't choose discard, it's empty")
                return None
            self.drawn = self.discard.pop()

        else:
            print("Invalid option")
            return None

        return self.drawn

    def place(self, player, loc):
        if(player != self.turn):
            print("Wrong player is going!")
            return None

        if self.drawn is None:
            print("You need to draw first!")

        loc = int(loc)

        # increment turn
        self.turn += 1
        if self.turn == self.n_players:
            self.turn = 0

        # swapping
        if loc < 6:
            # move swapped card into discard
            self.discard.append(self.hands[player][loc])
            self.discard[-1].hidden = False
            # put in drawn card
            self.hands[player][loc] = self.drawn

        # discarding
        else:
            to_flip = loc - 6
            # check if card is already flipped
            if self.hands[player][to_flip].hidden == False:
                print("Can't flip that card, it's already flipped")
                return None

            # otherwise discard and flip
            else:
                self.hands[player][to_flip].hidden = False
                self.discard.append(self.drawn)

        # check to see if that's the last turn!
        if (player+1)%self.n_players == self.ender:
            self.end_game()
            return "Done"

        # check if they finished the game
        if self.ender is None and sum([c.hidden for c in self.hands[player]]) == 0:
            print("You just flipped all your cards, game is ending")
            self.ender = player
            if self.n_players == 1:
                self.end_game()
                return "Done"

        self.drawn = None

        return True

    def end_game(self):
        # tally up scores
        scores = [sum([c.value for c in h]) for h in self.hands]

        # check for duplicate columns
        for i, h in enumerate(self.hands):
            for j in range(3):
                if h[j].face == h[j+3].face:
                    scores[i] -= 2*h[j].value

        # check if winner wasn't top score
        ender_score = scores[self.ender]
        if scores[self.ender] > min(scores):
            scores[self.ender] *= 2

        print()
        players = "\t".join([f"P{i}" for i in range(self.n_players)])
        print(players)
        print("\t".join([str(i) for i in scores]))

        self.winner = np.argmin(scores)
        return self.winner

    def print_board(self):
        # Print how close everyone is to finishing
        fl = ""
        sl = "hidden:"
        if self.n_players > 2:
            for i in range(self.n_players-2):
                player = (i+self.turn+2)%self.n_players
                fl += f"\tP{player}" 
                sl += f"\t{len([i for i in self.hands[player] if i.hidden])}"
            print(fl)
            print(sl)

        print("\nPILES", end='')
        piles = [self.deck[-1]]
        if len(self.discard) != 0:
            piles.append(self.discard[-1])
        print(View(piles))

        # print current hand
        print("\nYour Hand\t\t\tNext Player", end='')
        now = self.hands[self.turn]
        nex = self.hands[(self.turn+1)%self.n_players]

        for i in range(2):
            now_lst = View(now[i*3:(i+1)*3], spacing=-5)._merge_horizontal()
            nex_lst = View(nex[i*3:(i+1)*3], spacing=-5)._merge_horizontal()
            lst = [o + ["\t"] + e for o, e in zip(now_lst, nex_lst)]
            print(convert_layers_to_string(lst))
         
if __name__ == "__main__":
    g = Golf(2)
    done = False
    while not done:
        os.system('clear')
        g.print_board()
        
        print("Would you like to draw (0) or pickup discard (1)?")
        valid = None
        while valid is None:
            choice = input()
            valid = g.draw(0, choice)

        print("You drew", end='')
        print(valid)

        print("Choose what to do with it")
        print("Place \t Discard & Flip")
        print("0 1 2 \t 6  7  8")
        print("3 4 5 \t 9 10 11")
        valid = None
        while valid is None:
            choice = input()
            valid = g.place(0, choice)
        done = valid == "Done"

        # Now the computer goes
        valid = g.draw(1, 0)
        valid = g.place(1, randint(0,6))
        done = valid == "Done"
