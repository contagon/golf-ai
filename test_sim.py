from golf import Golf
import matplotlib.pyplot as plt
import numpy as np
from numpy.random import randint

n_players = 2
g = Golf(n_players)
while True:
    # iterate through each player
    for i in range(n_players):
        valid = None
        while valid is None:
            valid = g.draw(i, randint(0,2))

        valid = None
        while valid is None:
            valid = g.place(i, randint(0,12))

        if valid == "Done":
            break

    if valid == "Done":
        break

print("Winner is player ", g.winner)
