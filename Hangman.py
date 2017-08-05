# -*- coding: utf-8 -*-
"""
Created on Thu May 25 11:23:20 2017

@author: Jan
"""
import random
import string
import numpy as np
from numpy.random import choice
from collections import Counter
import datetime

class HangmanGame(object):
    
    def __init__(self, secretWord, guess_left=8):
        self.secretWord = secretWord
        self.lenght = len(self.secretWord)
        self.guess_left = guess_left
        self.letters_left = list(string.ascii_lowercase)
        self.guessed_letters = []
        self.guessedWord = HangmanGame.getGuessedWord(self.secretWord, self.guessed_letters)
        self.result = None
        
    def get_secretWord(self):
        return self.secretWord
            
    def get_lenght(self):
        return self.lenght
        
    def get_guess_left(self):
        return self.guess_left
        
    def get_letters_left(self):
        return self.letters_left
        
    def get_guessed_letters(self):
        return self.guessed_letters
        
    def get_guessedWord(self):
        return self.guessedWord
        
    def get_result(self):
        return self.result
        
    def getGuessedWord(secretWord, lettersGuessed):
        check = ""
        
        for i in secretWord:
            if i in lettersGuessed:
                check += i
            else:
                check += "_"
                
        return check
        
    def update(self, letter):
        self.letters_left.remove(letter)
        if letter not in self.secretWord:
            self.guess_left -= 1
            if self.get_guess_left() == 0:
                self.result = 0            
        else:
           self.guessed_letters.append(letter)
           self.guessedWord = HangmanGame.getGuessedWord(self.secretWord, self.guessed_letters)

           if self.get_secretWord() == self.get_guessedWord():
               self.result = 1
               
class HangmanPlayer(object):
    """Abstract player class"""
    def __init__(self):
        self.results = []
        
    def get_result(self):
        return self.results
        
    def get_score(self):
        return np.array(self.results).mean()
        
    def set_game(self, wordlist, guess_left=8):
        secretWord = random.choice(wordlist)
        self.game = HangmanGame(secretWord, guess_left)
        
    def guess(self):
        raise NotImplementedError
        
    def play_game(self):
        while True:
            self.guess()
            if self.game.get_result() == 1:
                self.results.append(1)
                break
            if self.game.get_result() == 0:
                self.results.append(0)
                break

class UniRandomPlayer(HangmanPlayer):
    def __str__(self):
        return "UniRandomPlayer"
        
    def guess(self):
        g = random.choice(self.game.get_letters_left())
        self.game.update(g)
        
class LetterFreqPlayer(HangmanPlayer):
    def __str__(self):
        return "LetterFreqPlayer"
    
    def guess(self):
        self.game.update(self.gs.pop(0))
        
    def set_game(self, wordlist):
        self.gs = list("etaoinshrdlcumwfgypbvkjxqz")
        HangmanPlayer.set_game(self, wordlist)
                
class RandomFreqPlayer(HangmanPlayer):
    def __str__(self):
        return "RandomFreqPlayer"
        
    def __init__(self):
        self.gs = list("etaoinshrdlcumwfgypbvkjxqz")
        self.weights = [0.12702,0.09056,0.08167,0.07507,0.06966,0.06749,
                        0.06327,0.06094,0.05987,0.04253,0.04025,0.02782,
                        0.02758,0.02406,0.02360,0.02228,0.02015,0.01974,
                        0.01929,0.01492,0.00978,0.00772,0.00153,0.00150,
                        0.00095,0.00074]
        self.results = []
    
    def guess(self):
        try:
            self.game.update(choice(self.gs, 1, self.weights)[0])
        except:
            "do nothing"
            
class CombFreqPlayer(LetterFreqPlayer):
    def __str__(self):
        return "CombFreqPlayer(%i)" %self.k
        
    def __init__(self, k=15):
        self.k = k
        self.results = []
        
    def set_game(self, wordlist):
        self.count = 0
        LetterFreqPlayer.set_game(self, wordlist)
        
    def guess(self):
        if self.count < self.k:
            LetterFreqPlayer.guess(self)
        else:
            UniRandomPlayer.guess(self)
        self.count += 1
        
class BrutePlayer(HangmanPlayer):
    def __str__(self):
        return "BrutePlayer"
    
    def set_game(self, wordlist):
        self.wordlist = np.array(wordlist)
        HangmanPlayer.set_game(self, wordlist)
            
    def compare(word, secretWord):
        if len(word) != len(secretWord):
            return False
        for i in range(len(word)):
            if word[i] != secretWord[i] and secretWord[i] != "_":
                return False
        return True
        
    f = np.vectorize(compare)
                        
    def guess(self):
        ids = BrutePlayer.f(self.wordlist, self.game.get_guessedWord())
        poss = self.wordlist[ids]
        c = Counter("".join(list(poss)))
        gs = []
        for letter in self.game.get_letters_left():
            gs.append((c[letter], letter))
        gs.sort()
        self.game.update(gs[-1][1])
        
class SmartPlayer(HangmanPlayer):
    def __str__(self):
        return "SmartPlayer(k=%i)"%self.k
        
    def __init__(self, k=3):
        self.k = k
        self.results = []
        
    def set_game(self, wordlist):
        self.gs = list("etaoinshrdlcumwfgypbvkjxqz")
        BrutePlayer.set_game(self, wordlist)
        
    def guess(self):
        if self.game.get_guess_left() > self.k:
            LetterFreqPlayer.guess(self)
        else:
            BrutePlayer.guess(self)
                
class HumanPlayer(HangmanPlayer):
    def __str__(self):
        return "HumanPlayer"
    
    def guess(self):
        print("")
        print("You have %s guesses left."%self.game.get_guess_left())
        print("Letters unused: %s" %self.game.get_letters_left())
        print("Your word: %s"%self.game.get_guessedWord())
        g = input("Please guess a letter: ")
        try:
            self.game.update(g)
        except:
            print("Oops! You've already guessed that letter: %s"%g)
        
    def play_game(self):
        print("")
        print("Welcome to the game, Hangman!")
        print("I am thinking of a word that is %s letters long."%self.game.get_lenght())
        print("-----------")
        while True:
            self.guess()
            if self.game.get_result() == 1:
                self.results.append(1)
                print("Congratulations, you won!")
                break
            if self.game.get_result() == 0:
                self.results.append(0)
                print("Sorry, you ran out of guesses. The word: %s"%self.game.get_secretWord())
                break
            
def loadWords():
    print("")
    print("Loading word list from file...")
    # inFile: file
    inFile = open("words.txt", 'r')
    # wordList: list of strings
    wordList = []
    for line in inFile:
        wordList.append(line.strip().lower())
    print("  ", len(wordList), "words loaded.")
    return wordList

            
def human_play(wordlist):
    p = HumanPlayer()
    while True:
        p.set_game(wordlist)
        p.play_game()
        i = input("Wanna play again? (y/n) ")
        if i == "n":
            break
            
def test_players(wordlist, players, num_simuls):
    print("")
    print("Testing %i players, #simulations: %i." %(len(players), num_simuls))
    tt = datetime.datetime.now()
    num = 1
    for player in players:
        t0 = datetime.datetime.now()
        print("")
        print("Player%i:"%num, player)
        for _ in range(num_simuls):
            player.set_game(wordlist)
            player.play_game()
        print("Score:", player.get_score())
        print("Test duration:", datetime.datetime.now()-t0)
        num += 1
    print("")
    print("Total duration:", datetime.datetime.now()-tt)
        
if __name__ in "__main__":
    wordlist = loadWords()
    
#    num_simuls = 10000    
#    players =[
#    UniRandomPlayer(),
#    RandomFreqPlayer(),
#    LetterFreqPlayer(),
#    CombFreqPlayer(), 
#    BrutePlayer(),
#    SmartPlayer()
#             ]
    
#    num_simuls = 100
#    players = [SmartPlayer(k) for k in range(9)]
#   
    num_simuls = 10000
    players = [CombFreqPlayer(k) for k in range(27)]
#    
    test_players(wordlist, players, num_simuls) 