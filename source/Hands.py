from collections import defaultdict


class Hand(object):
    """the best can produce with the cards available"""
    def __init__(self, cards):
        self.cards = cards

    def __iter__(self):
        return self.cards.__iter__()

    def __lt__(self, other):
        return not self.__ge__(other)

    def __gt__(self, other):

        for rank in handRanking:
            if rank(self.cards) and rank(other.cards):
                return rank(self.cards) > rank(other.cards)

            if rank(self.cards):
                return True

            if rank(other.cards):
                return False

        return False

    def __eq__(self, other):

        if self.cards == [] and other.cards == []:
            return True

        for rank in handRanking:
            if rank(self.cards) and rank(other.cards):
                if rank(self.cards) == rank(other.cards):
                    return True

        return False

    def __le__(self, other):
        return not self.__gt__(other)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def rank(self):
        match = first(handRanking, self.cards)
        hand = ','.join([str(card) for card in match(self.cards)])
        return hand + ' ' + match.__name__


def first(conditions, cards):
    for c in conditions:
        if c(cards):
            return c


def highestCard(hand):
    return sorted(hand, key=lambda card: card.value, reverse=True)[0:5]


def pair(hand):

    values = map(lambda card: card.value, hand)
    pairs = [card for card in hand if values.count(card.value) == 2]

    if len(pairs) == 2:
        return pairs


def pairHand(hand):

    if pair(hand):
        remaining = [card for card in hand if card not in pair(hand)]

        return pair(hand) + highestCard(remaining)[0:3]


def twoPair(hand):

    pairs = [card for card in hand if hand.count(card) == 2]
    pairs = sorted(pairs, reverse=True)

    if len(pairs) >= 4:
        return pairs[0:4]


def twoPairHand(hand):

    cards = twoPair(hand)

    if cards:
        remaining = [card for card in hand if card not in cards]
        return cards + [max(remaining)]


def trips(hand):

    values = map(lambda card: card.value, hand)
    result = [card for card in hand if values.count(card.value) == 3]

    return result


def tripHand(hand):

    match = trips(hand)
    if match:
        hand = [card for card in hand if card not in match]
        hand = match + highestCard(hand)[0:2]
        return hand


def poker(hand):
    values = map(lambda card: card.value, hand)
    pokerHand = [card for card in hand if values.count(card.value) == 4]

    return pokerHand


def pokerHand(hand):

    match = poker(hand)

    if match:
        hand = [card for card in hand if card not in match]
        return match + [highestCard(hand)[0]]


def flush(hand):

    flush = flushCards(hand)

    if flush:
        return sorted(flush, key=lambda card: card.value, reverse=True)[0:5]


def flushCards(hand):
    suits = map(lambda card: card.suit, hand)
    flush = [card for card in hand if suits.count(card.suit) >= 5]

    return flush


def distinctValue(cards):

    distinctValue = defaultdict(list)

    for card in cards:
        distinctValue[card.value].append(card)

    cards = [(distinctValue[k][0]) for k in distinctValue]

    return cards


def straight(cards):

    cards = distinctValue(cards)
    cards = sorted(cards, key=lambda card: card.value, reverse=True)

    while len(cards) >= 5:

        if cards[0].value - cards[4].value == 4:
            return cards[0:5]

        cards = cards[1:]


def straightFlush(cards):

    return straight(flushCards(cards))


def house(cards):

    if not trips(cards):
        return

    hand = trips(cards)

    cards = [card for card in cards if card not in hand]
    if not pair(cards):
        return

    return hand + pair(cards)


handRanking = [straightFlush, pokerHand, house,
               flush, straight, tripHand,
               twoPairHand, pairHand, highestCard]
