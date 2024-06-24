import json
from crossword.puzzle import CrosswordPuzzle

puzzle_name = 'test'
title = 'Title'
subtitle = 'Subtitle'

with open('data.json', 'r') as f:
    data = json.load(f)[puzzle_name]

words = list(data.keys())
clues = list(data.values())
num_words = len(words)

CrosswordPuzzle(title, subtitle, words, clues, scale_factor=1, max_depth=num_words, autogen=True, show_solution=False).generate2D()
CrosswordPuzzle(title, subtitle, words, clues, scale_factor=1, max_depth=num_words, autogen=True, show_solution=False).generate3D()