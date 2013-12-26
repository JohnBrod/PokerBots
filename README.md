PokerBots
=========

A poker tournament for computer programs

Setup:
============

Python

1) Install openfire server.

2) Set up the accounts. 
You'll need an account for each player and these two other accounts:
    - The dealer: this account is the main contact point for the players. He'll send out the cards and take their bets.
    - The audience: this account receives all the public information. It can be used to give the outside world a view on whats happening in the game.

3) How to write a player

 - download a suitable third party XMPP library
 - Send these messages to the dealer
  - your jid to join
  - the only message you repsond to is GO. Respond with 0 (to fold, or check) or in the range min bet to all your chips
 - Handle the following messages from the dealer
  - GO, indicates you need to respond with a bet
  - BET, tells you that a player bet
  - WON, tells you the result of the hand
  - DEALING, tells you what players are in the hand
  - CHIPS, at the start of the game, tells you the amount of chips you and the other players have
  - CARD, one or more cards that you can use to form a hand

4) Sample conversation between player1 and dealer:

player: player1@pokerchat                                                 # sending jid to the dealer to join the game
dealer: CHIPS 1000                                                        # dealer tells you how many chips you have
dealer: DEALING player1@pokerchat, player2@pokerchat                      # dealer announces the players being dealt to
dealer: CARD 10H 4H                                                       # dealer sends out private cards
dealer: GO                                                                # dealer tells player to place a bet
player: 100                                                               # player bets 100
dealer: BET player1@pokerchat 100                                         # dealers announces player1's bet
dealer: BET player2@pokerchat 100                                         # dealers announces player2 has called
dealer: CARD 9H 11H 12H                                                   # community cards are dealt
dealer: GO                                                                # dealer tells player to place a bet
player: 100                                                               # player bets 100
dealer: BET player1@pokerchat 100                                         # dealers announces player1's bet
dealer: BET player2@pokerchat 0                                           # dealers announces player2 has folded
dealer: WON player1@pokerchat player1@pokerchat 100 10H 4H 9H 11H 12H     # player1 wins back 100
dealer: WON player1@pokerchat player2@pokerchat 100 10H 4H 9H 11H 12H     # player1 wins 100 from player2
dealer: WON player2@pokerchat player2@pokerchat 0 6S 2C 9H 11H 12H        # player2 wins back 0
dealer: WON player2@pokerchat player1@pokerchat 0 6S 2C 9H 11H 12H        # player2 wins 0 from player1

5) Starting the game

PokerGame --d dealer@pokerchat -p password -a audience@pokerchat -c 1000 -w 30 -o localhost -r 5222