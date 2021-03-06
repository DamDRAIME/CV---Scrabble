"""
A Python implementation of the famous board game: Scrabble.
"""

import math
import random
import string

HAND_SIZE = 7

SCRABBLE_LETTER_VALUES = {
    "A": 1,
    "B": 3,
    "C": 3,
    "D": 2,
    "E": 1,
    "F": 4,
    "G": 2,
    "H": 4,
    "I": 1,
    "J": 8,
    "K": 5,
    "L": 1,
    "M": 3,
    "N": 1,
    "O": 1,
    "P": 3,
    "Q": 10,
    "R": 1,
    "S": 1,
    "T": 1,
    "U": 1,
    "V": 4,
    "W": 4,
    "X": 8,
    "Y": 4,
    "Z": 10,
    "*": 0,
}

WORDLIST_FILENAME = "words.txt"


class BagOfTiles:
    def __init__(self):
        tiles_values = list(string.ascii_uppercase + "*")
        tiles_freq = [9, 2, 2, 4, 12, 2, 3, 2, 9, 9, 1, 4, 2,  # A -> M
                      6, 8, 2, 1, 6, 4, 6, 4, 2, 2, 1, 2, 1,  # N -> Z
                      2]  # Joker
        self.tiles = [value
                      for value, freq in zip(tiles_values, tiles_freq)
                      for _ in range(freq)]
        self.empty = False
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.tiles)

    def get_tiles(self, x):
        t = []
        try:
            for _ in range(x):
                t.append(self.get_tile())
        except StopIteration:
            print("Bag is empty and doesn't contain anymore tiles!")
        finally:
            return t

    def get_tile(self):
        if not self.empty:
            t = self.tiles.pop()
            self.empty = False if self.tiles else True
            return t
        else:
            self.empty = True
            raise StopIteration

    def replace_tiles(self, tiles_to_replace):
        assert not self.empty, 'The bag is empty'
        assert len(tiles_to_replace) < len(self.tiles), \
            'There are not that many tiles left in the bag. \n' \
            'Number of tiles in the bag: {}'.format(len(self.tiles))

        new_tiles = self.get_tiles(len(tiles_to_replace))
        self.tiles.extend(tiles_to_replace)
        self.shuffle()
        return new_tiles

    def show(self):
        print(self.tiles)

def load_words():
    """
    Returns a list of valid words. Words are strings of lowercase letters.
    
    Depending on the size of the word list, this function may
    take a while to finish.
    """

    print("Loading word list from file...")
    # inFile: file
    inFile = open(WORDLIST_FILENAME, "r")
    # wordlist: list of strings
    wordlist = []
    for line in inFile:
        wordlist.append(line.strip().lower())
    print("  ", len(wordlist), "words loaded.")
    return wordlist


def get_frequency_dict(sequence):
    """
    Returns a dictionary where the keys are elements of the sequence
    and the values are integer counts, for the number of times that
    an element is repeated in the sequence.

    sequence: string or list
    return: dictionary
    """

    # freqs: dictionary (element_type -> int)
    freq = {}
    for x in sequence:
        freq[x] = freq.get(x, 0) + 1
    return freq


# (end of helper code)
# -----------------------------------

#
# Problem #1: Scoring a word
#
def get_word_score(word, n):
    """
    Returns the score for a word. Assumes the word is a
    valid word.

    You may assume that the input word is always either a string of letters, 
    or the empty string "". You may not assume that the string will only contain 
    lowercase letters, so you will have to handle uppercase and mixed case strings 
    appropriately. 

    The score for a word is the product of two components:

    The first component is the sum of the points for letters in the word.
    The second component is the larger of:
            1, or
            7*wordlen - 3*(n-wordlen), where wordlen is the length of the word
            and n is the hand length when the word was played

    Letters are scored as in Scrabble; A is worth 1, B is
    worth 3, C is worth 3, D is worth 2, E is worth 1, and so on.

    word: string
    n: int >= 0
    returns: int >= 0
    """

    score = 0
    word = word.lower()
    for letter in word:
        score += SCRABBLE_LETTER_VALUES[letter]
    score *= max(1, (7 * len(word) - 3 * (n - len(word))))
    return score


#
# Make sure you understand how this function works and what it does!
#
def display_hand(hand):
    """
    Displays the letters currently in the hand.

    For example:
       display_hand({'a':1, 'x':2, 'l':3, 'e':1})
    Should print out something like:
       a x x l l l e
    The order of the letters is unimportant.

    hand: dictionary (string -> int)
    """

    for letter in hand.keys():
        for j in range(hand[letter]):
            print(letter, end=" ")  # print all on the same line
    print()  # print an empty line


#
# Make sure you understand how this function works and what it does!
# You will need to modify this for Problem #4.
#
def deal_hand(n):
    """
    Returns a random hand containing n lowercase letters.
    ceil(n/3) letters in the hand should be VOWELS (note,
    ceil(n/3) means the smallest integer not less than n/3).

    Hands are represented as dictionaries. The keys are
    letters and the values are the number of times the
    particular letter is repeated in that hand.

    n: int >= 0
    returns: dictionary (string -> int)
    """

    hand = {}
    num_vowels = int(math.ceil(n / 3))

    for i in range(num_vowels - 1):
        x = random.choice(VOWELS)
        hand[x] = hand.get(x, 0) + 1

    for i in range(num_vowels, n):
        x = random.choice(CONSONANTS)
        hand[x] = hand.get(x, 0) + 1

    if n > 0:
        hand["*"] = 1

    return hand


#
# Problem #2: Update a hand by removing letters
#
def update_hand(hand, word):
    """
    Does NOT assume that hand contains every letter in word at least as
    many times as the letter appears in word. Letters in word that don't
    appear in hand should be ignored. Letters that appear in word more times
    than in hand should never result in a negative count; instead, set the
    count in the returned hand to 0 (or remove the letter from the
    dictionary, depending on how your code is structured). 

    Updates the hand: uses up the letters in the given word
    and returns the new hand, without those letters in it.

    Has no side effects: does not modify hand.

    word: string
    hand: dictionary (string -> int)    
    returns: dictionary (string -> int)
    """

    word = word.lower()
    new_hand = hand.copy()
    for letter in word:
        if new_hand.get(letter, 0) > 0:
            new_hand[letter] -= 1
    return new_hand


#
# Problem #3: Test word validity
#
def is_valid_word(word, hand, word_list):
    """
    Returns True if word is in the word_list and is entirely
    composed of letters in the hand. Otherwise, returns False.
    Does not mutate hand or word_list.
   
    word: string
    hand: dictionary (string -> int)
    word_list: list of lowercase strings
    returns: boolean
    """

    word = word.lower()
    dic_word = get_frequency_dict(word)
    for letter in dic_word.keys():
        if dic_word[letter] > hand.get(letter, 0):
            return False
    if word.find("*") == -1:
        for validword in word_list:
            if word == validword:
                return True
    else:
        for validword in word_list:
            for vowel in VOWELS:
                if word.replace("*", vowel) == validword:
                    return True
    return False


#
# Problem #5: Playing a hand
#
def calculate_handlen(hand):
    """ 
    Returns the length (number of letters) in the current hand.
    
    hand: dictionary (string-> int)
    returns: integer
    """

    len = 0
    for letter in hand:
        len += hand[letter]
    return len


def play_hand(hand, word_list):
    """
    Allows the user to play the given hand, as follows:

    * The hand is displayed.
    
    * The user may input a word.

    * When any word is entered (valid or invalid), it uses up letters
      from the hand.

    * An invalid word is rejected, and a message is displayed asking
      the user to choose another word.

    * After every valid word: the score for that word is displayed,
      the remaining letters in the hand are displayed, and the user
      is asked to input another word.

    * The sum of the word scores is displayed when the hand finishes.

    * The hand finishes when there are no more unused letters.
      The user can also finish playing the hand by inputing two 
      exclamation points (the string '!!') instead of a word.

      hand: dictionary (string -> int)
      word_list: list of lowercase strings
      returns: the total score for the hand
      
    """

    hand_score = 0

    while calculate_handlen(hand) > 0:
        print("Current hand: "), display_hand(hand)
        user_input = input('Enter word, or "!!" to indicate that you are finished: ')
        if user_input == "!!":
            break
        elif is_valid_word(user_input, hand, word_list):
            hand_score += get_word_score(user_input, HAND_SIZE)
            print(
                '"',
                user_input,
                '" earned ',
                get_word_score(user_input, HAND_SIZE),
                " points. Total: ",
                hand_score,
            )
            hand = update_hand(hand, user_input)
        else:
            print("This is not a valid word. Please choose another word.")

    print("Total score for this hand: ", hand_score)

    return hand_score

    print("--------------")


#
# Problem #6: Playing a game
#


#
# procedure you will use to substitute a letter in a hand
#


def substitute_hand(hand, letter):
    """ 
    Allow the user to replace all copies of one letter in the hand (chosen by user)
    with a new letter chosen from the VOWELS and CONSONANTS at random. The new letter
    should be different from user's choice, and should not be any of the letters
    already in the hand.

    If user provide a letter not in the hand, the hand should be the same.

    Has no side effects: does not mutate hand.

    For example:
        substitute_hand({'h':1, 'e':1, 'l':2, 'o':1}, 'l')
    might return:
        {'h':1, 'e':1, 'o':1, 'x':2} -> if the new letter is 'x'
    The new letter should not be 'h', 'e', 'l', or 'o' since those letters were
    already in the hand.
    
    hand: dictionary (string -> int)
    letter: string
    returns: dictionary (string -> int)
    """

    new_hand = hand
    if hand.get(letter, 0) != 0:
        list_letter = VOWELS + CONSONANTS
        for key in hand.keys():
            list_letter = list_letter.replace(key, "")
        new_letter = random.choice(list_letter)
        new_hand[new_letter] = hand[letter]
        del new_hand[letter]
    return new_hand


def play_game(word_list):
    """
    Allow the user to play a series of hands

    * Asks the user to input a total number of hands

    * Accumulates the score for each hand into a total score for the 
      entire series
 
    * For each hand, before playing, ask the user if they want to substitute
      one letter for another. If the user inputs 'yes', prompt them for their
      desired letter. This can only be done once during the game. Once the
      substitute option is used, the user should not be asked if they want to
      substitute letters in the future.

    * For each hand, ask the user if they would like to replay the hand.
      If the user inputs 'yes', they will replay the hand and keep 
      the better of the two scores for that hand.  This can only be done once 
      during the game. Once the replay option is used, the user should not
      be asked if they want to replay future hands. Replaying the hand does
      not count as one of the total number of hands the user initially
      wanted to play.

            * Note: if you replay a hand, you do not get the option to substitute
                    a letter - you must play whatever hand you just had.
      
    * Returns the total score for the series of hands

    word_list: list of lowercase strings
    """

    total_score = 0
    nbr_hand = int(input("Enter a number of hands: "))
    while nbr_hand > 0:
        hand = deal_hand(HAND_SIZE)
        display_hand(hand)
        substitute = input("Would you like to substitute a letter? ")
        if substitute.lower() == "yes":
            letter = input("Which letter would you like to replace? ")
            if len(letter) == 1:
                substitute_hand(hand, letter.lower())
            else:
                print("Not a valid input")
        elif substitute.lower() != "no":
            print("Not a valid input")

        total_score += play_hand(hand, word_list)
        nbr_hand -= 1

    print("Total score over all hands: ", total_score)


bol = BagOfTiles()
bol.show()
for _ in range(100):
    bol.get_tile()
bol.show()
print(bol.get_tiles(4))
bol.show()
bol.replace_tiles(['X', 'X', 'X'])
bol.show()
