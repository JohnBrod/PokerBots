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
  - JOIN to join a game. You will get a CHIPS response with the number of chips e.g. CHIPS 1000 
 - Handle the following messages from the dealer
  - GO, indicates you need to respond with a bet. Respond with less than min bet to fold or check. Respond in the range min bet to all your chips to bet.
  - BET, tells you that a player has bet. 
    - e.g. 'BET player1@pokerchat 100' player1@pokerchat has bet 100
  - WON, tells you the result of the hand 
    - e.g. 'WON player1@pokerchat player2@pokerchat 100 3S,3D,3H,6S,6D house' player1@pokerchat won 100 from player2@pokerchat with a house 
  - DEALING, tells you what players are in the hand
    - e.g. 'DEALING player1@pokerchat player2@pokerchat player3@pokerchat' starting a game with these three players
  - CHIPS, at the start of the game, tells you the amount of chips you and the other players have
    - e.g. 'CHIPS 1000' you have been accepted into the game and have 1000 chips
  - CARD, one or more cards that you can use to form a hand
    - e.g. 'CARD 3S 3D' you have bee dealt these cards. The first time it will be private cards, then public.
  - WINNER, the tournament is over
    - e.g. 'WINNER player1@pokerchat 2000' player1@pokerchat won the game with 2000 chips

4) Sample conversation between player1 and dealer:

player: JOIN                                                              # join the game
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

5) The audience

The audience is not part of the game but receives messages from the dealer to give a picture of everything that is happening in the game.

6) Starting the game

PokerGame --d dealer@pokerchat -p password -a audience@pokerchat -c 1000 -w 30 -o localhost -r 5222

The accounts dealer@pokerchat and audience@pokerchat are mandatory accounts but can be called anything. The dealer account will be used to deal cards to players and take bets from the players. The audience gives a public view into the game. See the file PokerGame.py for info on these optional parameters.