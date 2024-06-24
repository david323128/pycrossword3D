from crossword.word import Word3D
import math
from collections import deque


class Cube:

    def __init__(self, words, scale_factor, empty_space='-', max_depth=5):
        self.word_list = sorted(words, key=len, reverse=True)
        self.empty_space = empty_space
        self.num_words = len(words)
        self.words = self.init_words()
        self.pivot_word = self.words[0]
        self.pivot_word_length = self.pivot_word.length
        self.length = math.floor(self.pivot_word_length * scale_factor)
        self.cube = self.init_cube(empty_space)
        self.cube_count = self.init_cube(0)
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
            return [z*self.length**2 for z in range(self.length)]

        n = self.length
        coordinates = [(x, y, z) for x in range(self.max_length) for y in range(n) for z in range(n)]
        positions = [z*n**2 + y*n + x for (x, y, z) in coordinates]

        if not centered:
            return positions
        
        centered_positions = []

        for (p1,p2) in zip(positions[:len(positions)//2][::-1], positions[len(positions)//2:]):
            centered_positions.append(p1)
            centered_positions.append(p2)

        return centered_positions
        
    def init_words(self, words=[]):
        words = self.word_list if not words else words
        word_objects = {}
        for i, word in enumerate(words):
            word_obj = Word3D(word, i)
            if (i + 1) % 2 == 0:
                word_obj.rotate()
            word_objects[i] = word_obj
        return word_objects
    
    def init_cube(self, value):
        cube = {}
        for k in range(self.length):
            layer = {}
            for j in range(self.length):
                row = {}
                for i in range(self.length):
                    row[i] = value
                layer[j] = row
            cube[k] = layer
        return cube

    def update_cube(self, word):
        for i in range(word.length):
            self.cube[word.z + i * word.z_sign][word.y + i * word.y_sign][word.x + i * word.x_sign] = word.value[i]

    def reset(self):
        self.depth = 0
        self.words = self.init_words()
        self.inserted_indexes = set()
        self.cube_count = self.init_cube(0)
        self.cube = self.init_cube(self.empty_space)

    def increment_cube_count(self, word):
        for i in range(word.length):
            x = word.x + i * word.x_sign
            y = word.y + i * word.y_sign
            z = word.z + i * word.z_sign
            self.cube_count[z][y][x] += 1

    def decrement_cube_count(self, word):
        for i in range(word.length):
            x = word.x + i * word.x_sign
            y = word.y + i * word.y_sign
            z = word.z + i * word.z_sign
            if self.cube_count[z][y][x] > 0:
                self.cube_count[z][y][x] -= 1

    def print_cube(self):
        print('---Start Cube---')
        for k in range(self.length):
            print(f'Layer {k}')
            for j in range(self.length):
                row = ''
                for i in range(self.length):
                    row += self.cube[k][j][i]
                print(row)
            print('\n')
        print('---End Cube---')

    def check_word_ends(self, word):
        x_sign, y_sign, z_sign = word.x_sign, word.y_sign, word.z_sign
        max_len = self.length - 1

        x_prev = word.x - x_sign
        y_prev = word.y - y_sign
        z_prev = word.z - z_sign
        x_next = word.x + x_sign*word.length
        y_next = word.y + y_sign*word.length
        z_next = word.z + z_sign*word.length

        first_letter = word.value[0]
        last_letter = word.value[-1]
        prev_letter = self.cube[max(z_prev, 0)][max(y_prev, 0)][max(x_prev, 0)]
        next_letter = self.cube[min(z_next, max_len)][min(y_next, max_len)][min(x_next, max_len)]


        if x_prev < 0 and y_prev < 0 and z_prev < 0:
            if prev_letter != first_letter and prev_letter != self.empty_space:
                return False
        
        if x_prev >= 0 and y_prev >= 0 and z_prev >= 0:
            if prev_letter != self.empty_space:
                return False
        
        if x_next > max_len and y_next > max_len and z_next > max_len:
            if next_letter != last_letter and next_letter != self.empty_space:
                return False
        
        if x_next <= max_len and y_next <= max_len and z_next <= max_len:
            if next_letter != self.empty_space:
                return False
        return True
    
    def get_intersections(self, x_test, y_test, z_test, test_orientation, direction):
        u_sign, v_sign, w_sign = test_orientation
        starting_coordinattes = None
        letters = ''

        if self.is_valid_position(x_test, y_test, z_test):
            min_space = self.cube[z_test][y_test][x_test]
            if min_space != self.empty_space:
                xk = x_test
                yk = y_test
                zk = z_test

                while self.is_valid_position(xk, yk, zk) and self.cube[zk][yk][xk] != self.empty_space:
                    if not starting_coordinattes and direction != 1:
                        starting_coordinattes = (xk, yk, zk)
                    letters += self.cube[zk][yk][xk]
                    xk += direction*u_sign
                    yk += direction*v_sign
                    zk += direction*w_sign
        return letters[::direction], starting_coordinattes
    
    def check_insertion(self, word, offset, recursive=True):
        x_sign = word.x_sign
        y_sign = word.y_sign
        z_sign = word.z_sign
        x, y, z = word.x, word.y, word.z

        length = word.length - 1

        if not self.is_valid_position(x + length*x_sign, y + length*y_sign, z + length*z_sign):
            return False

        x_min = x
        y_min = y
        z_min = z
        x_max = x
        y_max = y
        z_max = z
        

        new_intersections = []

        # No end-to-end words
        if not self.check_word_ends(word):
            return False
        
        for i in range(word.length):
            if i == offset:
                continue

            # A and B directions are perpendicular to word orientation.
            
            # Side A
            xi_min_a = x_min + i*x_sign - y_sign
            yi_min_a = y_min + i*y_sign - z_sign
            zi_min_a = z_min + i*z_sign - x_sign

            xi_max_a = x_max + i*x_sign + y_sign
            yi_max_a = y_max + i*y_sign + z_sign
            zi_max_a = z_max + i*z_sign + x_sign

            orientation_a = (y_sign, z_sign, x_sign)

            # Side B
            xi_min_b = x_min + i*x_sign - z_sign
            yi_min_b = y_min + i*y_sign - x_sign
            zi_min_b = z_min + i*z_sign - y_sign

            xi_max_b = x_max + i*x_sign + z_sign
            yi_max_b = y_max + i*y_sign + x_sign
            zi_max_b = z_max + i*z_sign + y_sign

            orientation_b = (z_sign, x_sign, y_sign)

            backward = -1
            forward = 1

            letters_a_min, coordinates_a = self.get_intersections(xi_min_a, yi_min_a, zi_min_a, orientation_a, backward)
            letters_a_max, _ = self.get_intersections(xi_max_a, yi_max_a, zi_max_a, orientation_a, forward)
            letters_b_min, coordinates_b = self.get_intersections(xi_min_b, yi_min_b, zi_min_b, orientation_b, backward)
            letters_b_max, _ = self.get_intersections(xi_max_b, yi_max_b, zi_max_b, orientation_b, forward)

            word_letter = word.value[i]

            letters_a = letters_a_min + word_letter + letters_a_max
            letters_b = letters_b_min + word_letter + letters_b_max

            # Check inline.
            inline_space = self.cube[z + i*z_sign][y + i*y_sign][x + i*x_sign]
            if inline_space not in (word_letter, self.empty_space):
                return False

            len_letters_a = len(letters_a)
            len_letters_b = len(letters_b)

            matching_words_a, matching_words_b = [], []
            remaining_indexes = self.get_remaining_indexes()

            if len_letters_a > 1:
                for i in remaining_indexes:
                    remaining_word = self.words[i]
                    if remaining_word.value[:len_letters_a] == letters_a and i != word.index:
                        matching_words_a.append(remaining_word)
            if len_letters_b > 1:
                for i in remaining_indexes:
                    remaining_word = self.words[i]
                    if remaining_word.value[:len_letters_b] == letters_b and i != word.index:
                        matching_words_b.append(remaining_word)

            if len_letters_a > 1 and not matching_words_a:
                if letters_a not in self.word_list:
                    return False
            
            if len_letters_b > 1 and not matching_words_b:
                if letters_b not in self.word_list:
                    return False
            
            if coordinates_a:
                new_intersections.append((coordinates_a, orientation_a, matching_words_a))
            if coordinates_b:
                new_intersections.append((coordinates_b, orientation_b, matching_words_b))

        if recursive:
            return self.insert_intersections(new_intersections)
        return True

    def insert_intersections(self, intersections):
        for ((x, y, z), orientation, words) in intersections:
            for i,word in enumerate(words):
                if not self.insert_at(word, x, y, z, orientation):
                    for word in words[:i]:
                        self.remove(word)
                    return False
        return True
    
    def insert_pivot(self):
        while not self.pivot_word.x_sign:
            self.pivot_word.rotate()

        pivot_position = self.pivot_positions[self.pivot_index]

        pivot_length = self.pivot_word.length - 1
        x = pivot_position % max(self.max_length, 1)
        y = (pivot_position // self.length) % self.length
        z = pivot_position // (self.length * self.length)
            
        max_x = x + pivot_length * self.pivot_word.x_sign
        max_y = y + pivot_length * self.pivot_word.y_sign
        max_z = z + pivot_length * self.pivot_word.z_sign

        if not self.is_valid_position(max_x, max_y, max_z):
            return False
        
        self.pivot_index += 1
        self.pivot_word.update_position(x, y, z)

        self.update_cube(self.pivot_word)
        self.increment_cube_count(self.pivot_word)
        self.inserted_indexes.add(self.pivot_word.index)
        return True

    def insert_at(self, word, x, y, z, orientation):
        offset = 0 # Since inserting at (x, y, z)
        word.update_position(x, y, z)
        while word.get_orientation() != orientation:
            word.rotate()

        x_end = x + (word.length - 1)*word.x_sign
        y_end = y + (word.length - 1)*word.y_sign
        z_end = z + (word.length - 1)*word.z_sign
        if not self.is_valid_position(x_end, y_end, z_end):
            return False

        insertion_entry = word.generate_insertion_entry()
        if insertion_entry not in word.insertion_history and \
            self.check_insertion(word, offset, recursive=False):
                self.increment_cube_count(word)
                word.add_insertion_entry(insertion_entry)
                self.update_cube(word)
                self.inserted_indexes.add(word.index)
                return True
        return False

    def insert(self, word):
        if not self.inserted_indexes:
            return self.insert_pivot()
        
        inserted_indexes = set(self.inserted_indexes)
        
        for i in inserted_indexes:
            inserted_word = self.words[i]
            for j in range(inserted_word.length):
                for k in range(word.length):
                    if word.value[k] == inserted_word.value[j]:
                        if word.get_orientation() == inserted_word.get_orientation():
                            word.rotate()
                        x = inserted_word.x + j * inserted_word.x_sign
                        y = inserted_word.y + j * inserted_word.y_sign
                        z = inserted_word.z + j * inserted_word.z_sign
                        x_start = x - k * word.x_sign
                        y_start = y - k * word.y_sign
                        z_start = z - k * word.z_sign
                        x_end = x_start + (word.length - 1) * word.x_sign
                        y_end = y_start + (word.length - 1) * word.y_sign
                        z_end = z_start + (word.length - 1) * word.z_sign

                        if self.is_valid_position(x_start, y_start, z_start) and \
                            self.is_valid_position(x_end, y_end, z_end):
                            word.update_position(x_start, y_start, z_start)
                            offset = k
                            insertion_entry = word.generate_insertion_entry()

                            if insertion_entry not in word.insertion_history and \
                                self.check_insertion(word, offset):
                                    self.increment_cube_count(word)
                                    word.add_insertion_entry(insertion_entry)
                                    self.update_cube(word)
                                    self.inserted_indexes.add(word.index)
                                    return True
        return False
    
    def remove(self, word):
        length = word.length
        x_sign = word.x_sign
        y_sign = word.y_sign
        z_sign = word.z_sign
        x_pos = word.x
        y_pos = word.y
        z_pos = word.z

        for i in range(length):
            x = x_pos + i * x_sign
            y = y_pos + i * y_sign
            z = z_pos + i * z_sign

            if self.cube_count[z][y][x] == 1:
                self.cube[z][y][x] = self.empty_space
            
        if word.index in self.inserted_indexes:
            self.inserted_indexes.remove(word.index)
        self.decrement_cube_count(word)
        word.clear_position()

    def is_valid_position(self, x, y, z):
        return 0 <= x < self.length and 0 <= y < self.length and 0 <= z < self.length

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
                
                if num_inserted == 1 or self.depth > self.max_depth:
                    print(f'({self.pivot_index}/{self.num_pivots})Max Insertions: {max_inserted}/{self.num_words} @Pivot: {max_index}')
                    inserted_indexes = deque(maxlen=self.num_words)
                    self.reset()
                else:
                    self.remove(self.words[inserted_indexes.pop()])
                    self.depth += 1