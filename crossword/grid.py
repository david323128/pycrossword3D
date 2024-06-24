from crossword.word import Word2D
import math
from collections import deque


class Grid:

    def __init__(self, words, scale_factor, empty_space='-', max_depth=10):
        self.word_list = sorted(words, key=len, reverse=True)
        self.empty_space = empty_space
        self.num_words = len(words)
        self.words = self.init_words()
        self.pivot_word = self.words[0]
        self.pivot_word_length = self.pivot_word.length
        self.length = math.floor(self.pivot_word_length * scale_factor)
        self.grid = self.init_grid(empty_space)
        self.grid_count = self.init_grid(0)
        self.max_length = self.length - self.pivot_word_length
        self.pivot_positions = self.get_pivot_positions()
        self.num_pivots = len(self.pivot_positions) - 1
        self.pivot_index = 0
        self.depth = 0
        self.max_depth = max_depth
        self.indexes = set(range(self.num_words))
        self.inserted_indexes = set()

    def get_remaining_indexes(self):
        return self.indexes - self.inserted_indexes
    
    def get_pivot_positions(self, centered=True):
        if self.length == self.pivot_word_length:
            return [y*self.length for y in range(self.length)]
        
        coordinates = [(x, y) for x in range(self.max_length) for y in range(self.length)]
        positions = [y * self.length + x for (x, y) in coordinates]

        if not centered:
            return positions
        
        centered_positions = []
        
        for (p1,p2) in zip(positions[:len(positions)//2][::-1], positions[len(positions)//2:]):
            centered_positions.append(p1)
            centered_positions.append(p2)

        return centered_positions

    def init_words(self, words=[]):
        word_list = self.word_list if not words else words
        word_objects = {}
        for i, word in enumerate(word_list):
            word_obj = Word2D(word, i)
            if (i + 1) % 2 == 0:
                word_obj.rotate()
            word_objects[i] = word_obj
        return word_objects
          
    def init_grid(self, value):
        grid = {}
        for j in range(self.length):
            row = {}
            for i in range(self.length):
                row[i] = value
            grid[j] = row
        return grid
    
    def update_grid(self, word):
        for i in range(word.length):
            self.grid[word.y + i * word.y_sign][word.x + i * word.x_sign] = word.value[i]

    def reset(self):
        self.depth = 0
        self.words = self.init_words()
        self.inserted_indexes = set()
        self.grid_count = self.init_grid(0)
        self.grid = self.init_grid(self.empty_space)

    def increment_grid_count(self, word):
        for i in range(word.length):
            x = word.x + i * word.x_sign
            y = word.y + i * word.y_sign
            self.grid_count[y][x] += 1

    def decrement_grid_count(self, word):
        for i in range(word.length):
            x = word.x + i * word.x_sign
            y = word.y + i * word.y_sign
            if self.grid_count[y][x] > 0:
                self.grid_count[y][x] -= 1

    def print_grid(self):
        print('--- Start Grid ---')
        for j in range(self.length):
            row = ''
            for i in range(self.length):
                row += self.grid[j][i]
            print(row)
        print('--- End Grid --- ')

    def check_word_ends(self, word):
        x_sign, y_sign = word.x_sign, word.y_sign
        max_len = self.length - 1

        x_prev = word.x - x_sign
        y_prev = word.y - y_sign
        x_next = word.x + x_sign*word.length
        y_next = word.y + y_sign*word.length

        first_letter = word.value[0]
        last_letter = word.value[-1]
        prev_letter = self.grid[max(y_prev, 0)][max(x_prev, 0)]
        next_letter = self.grid[min(y_next, max_len)][min(x_next, max_len)]

        if x_prev < 0 and y_prev < 0:
            if prev_letter != first_letter and prev_letter != self.empty_space:
                return False
        
        if x_prev >= 0 and y_prev >= 0:
            if prev_letter != self.empty_space:
                return False
        
        if x_next > max_len and y_next > max_len:
            if next_letter != last_letter and next_letter != self.empty_space:
                return False
        
        if x_next <= max_len and y_next <= max_len:
            if next_letter != self.empty_space:
                return False
        return True

    def get_intersections(self, x_test, y_test, test_orientation, direction):
        u_sign, v_sign = test_orientation
        starting_coordinattes = None
        letters = ''

        if self.is_valid_position(x_test, y_test):
            min_space = self.grid[y_test][x_test]
            if min_space != self.empty_space:
                xk = x_test
                yk = y_test
                while self.is_valid_position(xk, yk) and self.grid[yk][xk] != self.empty_space:
                    if not starting_coordinattes and direction != 1:
                        starting_coordinattes = (xk, yk)
                    letters += self.grid[yk][xk]
                    xk += direction*u_sign
                    yk += direction*v_sign
        return letters[::direction], starting_coordinattes

    def check_insertion(self, word, offset, recursive=True):
        x_sign = word.x_sign
        y_sign = word.y_sign
        x, y = word.x, word.y

        if not self.is_valid_position(x + (word.length - 1)*x_sign, y + (word.length - 1)*y_sign):
            return False

        x_min = x - y_sign
        y_min = y - x_sign
        x_max = x + y_sign
        y_max = y + x_sign

        new_intersections = []

        # No end-to-end words
        if not self.check_word_ends(word):
            return False
        
        for i in range(word.length):
            if i == offset:
                continue

            # surrounding spaces except word ends
            xi_min = x_min + i*x_sign
            yi_min = y_min + i*y_sign
            xi_max = x_max + i*x_sign
            yi_max = y_max + i*y_sign

            orientation = (y_sign, x_sign) # Perpendicular to word

            backward = -1
            forward = 1

            letters_min, coordinates = self.get_intersections(xi_min, yi_min, orientation, backward)
            letters_max, _ = self.get_intersections(xi_max, yi_max, orientation, forward)

            word_letter = word.value[i]
            letters = letters_min + word_letter + letters_max
            inline_space = self.grid[y + i*y_sign][x + i*x_sign]

            if inline_space not in (word_letter, self.empty_space):
                return False
            
            len_letters = len(letters)

            if len_letters > 1:
                matching_words = []
                for i in self.get_remaining_indexes():
                    remaining_word = self.words[i]
                    if remaining_word.value[:len_letters] == letters and i != word.index:
                        matching_words.append(remaining_word)

            if len_letters > 1 and not matching_words:
                if letters not in self.word_list:
                    return False
            
            if coordinates:
                new_intersections.append((coordinates, orientation, matching_words))
        if recursive:
            return self.insert_intersections(new_intersections)
        return True
    
    def insert_intersections(self, intersections):
        for ((x, y), orientation, words) in intersections:
            for i,word in enumerate(words):
                if not self.insert_at(word, x, y, orientation):
                    for word in words[:i]:
                        self.remove(word)
                    return False
        return True

    def insert_pivot(self, pivot_word):
        if not pivot_word.x_sign:
            pivot_word.rotate()

        pivot_position = self.pivot_positions[self.pivot_index]
        pivot_length = pivot_word.length - 1

        x = pivot_position % max(self.max_length, 1)
        y = pivot_position // self.length

        x_max = x + pivot_length*pivot_word.x_sign
        y_max = y + pivot_length*pivot_word.y_sign

        if not self.is_valid_position(x_max, y_max):
            return False
        
        self.pivot_index += 1
        pivot_word.update_position(x, y)
        self.update_grid(pivot_word)
        self.increment_grid_count(pivot_word)
        self.inserted_indexes.add(pivot_word.index)
        return True

    def insert_at(self, word, x, y, orientation):
        offset = 0 # Since starting at (x, y)
        word.update_position(x, y)
        if word.get_orientation() != orientation:
            word.rotate()

        x_end, y_end = x + (word.length - 1)*word.x_sign, y + (word.length - 1)*word.y_sign
        if not self.is_valid_position(x_end, y_end):
            return False
        
        insertion_entry = word.generate_insertion_entry()

        if insertion_entry not in word.insertion_history and \
            self.check_insertion(word, offset, recursive=False):
                self.increment_grid_count(word)
                word.add_insertion_entry(insertion_entry)
                self.update_grid(word)
                self.inserted_indexes.add(word.index)
                return True
        return False

    def insert(self, word):
        if not self.inserted_indexes:
            return self.insert_pivot(word)

        for i in self.inserted_indexes:
            inserted_word = self.words[i]
            for j in range(inserted_word.length):
                for k in range(word.length):
                    if word.value[k] == inserted_word.value[j]:
                        if word.get_orientation() == inserted_word.get_orientation():
                            word.rotate()
                        x = inserted_word.x + j * inserted_word.x_sign
                        y = inserted_word.y + j * inserted_word.y_sign
                        x_start = x - k * word.x_sign
                        y_start = y - k * word.y_sign
                        x_end = x_start + (word.length - 1) * word.x_sign
                        y_end = y_start + (word.length - 1) * word.y_sign

                        if self.is_valid_position(x_start, y_start) and \
                            self.is_valid_position(x_end, y_end):
                            word.update_position(x_start, y_start)
                            offset = k
                            insertion_entry = word.generate_insertion_entry()
                            if insertion_entry not in word.insertion_history and \
                                self.check_insertion(word, offset):
                                    self.increment_grid_count(word)
                                    word.add_insertion_entry(insertion_entry)
                                    self.update_grid(word)
                                    self.inserted_indexes.add(word.index)
                                    return True
        return False
    
    def remove(self, word):
        length = word.length
        x_sign = word.x_sign
        y_sign = word.y_sign
        x_pos = word.x
        y_pos = word.y

        for i in range(length):
            x = x_pos + i * x_sign
            y = y_pos + i * y_sign

            if self.grid_count[y][x] == 1:
                self.grid[y][x] = self.empty_space
        
        self.inserted_indexes.remove(word.index)
        self.decrement_grid_count(word)
        word.clear_position()

    def is_valid_position(self, x, y):
        return 0 <= x < self.length and 0 <= y < self.length

    def generate(self):
        inserted_indexes = deque(maxlen=self.num_words)
        max_inserted = 0
        max_index = 0
        while self.pivot_index < self.num_pivots:
            remaining_indexes = self.get_remaining_indexes()
            insertions = False            

            for i in remaining_indexes:
                if self.insert(self.words[i]):
                    insertions = True
                    inserted_indexes.append(i)
                
            num_inserted = len(self.inserted_indexes)
            if num_inserted == self.num_words:
                return self.words.values()
            if not insertions:
                if num_inserted > max_inserted:
                    max_inserted = num_inserted
                    max_index = self.pivot_index
                self.remove(self.words[inserted_indexes.pop()])
                self.depth += 1
                if num_inserted == 1 or self.depth > self.max_depth:
                    print(f'({self.pivot_index}/{self.num_pivots})Max Insertions: {max_inserted}/{self.num_words} @Pivot: {max_index}')
                    inserted_indexes = deque(maxlen=self.num_words)
                    self.reset()
                
                         
