from jinja2 import Environment, FileSystemLoader
import os
from crossword.cube import Cube
from crossword.grid import Grid


class CrosswordPuzzle:

    """Generates a 2D or 3D printable crossword puzzle."""

    def __init__(self, 
                    title, 
                    subtitle, 
                    words,
                    clues,
                    scale_factor=1,
                    max_depth=5,
                    show_solution=False,
                    autogen=False,
                    ):
        
        self.title = title
        self.subtitle = subtitle
        self.words = words
        self.clues = clues
        self.scale_factor = scale_factor
        self.max_depth = max_depth
        self.show_solution = show_solution
        self.autogen = autogen

    def generate_guide_grid(self, length, crossword_grid, empty_space):
        grid = []
        for j in range(length):
            row = []
            for i in range(length):
                if crossword_grid[j][i] != empty_space:
                    row.append('+')
                else:
                    row.append('-')
            grid.append(row)
        return grid

    def generate_guide_cube(self, length, crossword_cube, empty_space):
        cube = []
        for k in range(length):
            plane = []
            for j in range(length):
                row = []
                for i in range(length):
                    if crossword_cube[k][j][i] != empty_space:
                        row.append('+')
                    else:
                        row.append('-')
                plane.append(row)
            cube.append(plane)
        return cube
    
    def number_words(self, words, length, dimension=2):
        numbered_words = set()
        if dimension == 2:
            position = lambda word: word.x + word.y*length
        else:
            position = lambda word: word.x + word.y*length + word.z*length**2
        sorted_words = sorted([(word, position(word)) for word in words], key=lambda x: x[1])
        prev_pos, prev_index = -1, -1
        for word,pos in sorted_words:
            if pos == prev_pos:
                word.index = prev_index
            else:
                word.index = max(prev_index + 1, 1)
            prev_pos = pos
            prev_index = word.index
            numbered_words.add(word)
        return numbered_words

    def generate2D(self):
        words = None

        while not words:
            crossword = Grid(self.words, self.scale_factor, max_depth=self.max_depth)
            words = crossword.generate()
            if not words:
                if not self.autogen:
                    print('2D puzzle could not be generated. Trying increasing recursion limit or scale factor.')
                    return None
                self.scale_factor += 0.1
                print(f'Increasing scale factor to {self.scale_factor}')
        
        length, empty_space, grid = crossword.length, crossword.empty_space, crossword.grid
        guide_grid = self.generate_guide_grid(length, grid, empty_space)

        html_grid = []

        for y in range(length):
            row = []
            for x in range(length):
                if guide_grid[y][x] == '+':
                    row.append('''
                                <div 
                                    class="row-item" 
                                    style="
                                        background: white;
                                        padding: 5px;
                                        color: white; 
                                        border: 1px solid black">
                                    / 
                                </div>'''
                                )
                else:
                    row.append('''
                                <div 
                                    class="row-item" 
                                    style="
                                        background: #727272;
                                        padding: 5px; 
                                        color: #727272; 
                                        border: 1px solid black">
                                    / 
                                </div>'''
                                )
            html_grid.append(row)

        across_clues = []
        down_clues = []
        across = "<br><b>Across</b><br>"
        down = "<br><b>Down</b><br>"

        numbered_words = self.number_words(words, length)

        for word in numbered_words:
            index = word.index

            if self.show_solution:
                for j,letter in enumerate(word.value):
                    x = word.x + j*word.x_sign
                    y = word.y + j*word.y_sign

                    html_grid[y][x] = f'''
                        <div 
                            class="row-item"
                            style="
                                background: white;
                                padding: 5px;
                                color: black; 
                                border: 1px solid grey">
                            {letter}
                        </div>'''
            else:
                html_grid[word.y][word.x] = f'''
                    <div 
                        class="row-item"
                        style="
                            background: white;
                            padding: 5px; 
                            color: black; 
                            border: 1px solid black">
                        {index}
                    </div>'''

            if word.x_sign:
                across_clues.append((index, f'<br>{index}. {self.clues[self.words.index(word.value)]}'))
            else:
                down_clues.append((index, f'<br>{index}. {self.clues[self.words.index(word.value)]}'))
                                  
        for (_,clue) in sorted(across_clues, key=lambda x: x[0]):
            across += clue
        for (_,clue) in sorted(down_clues, key=lambda x: x[0]):
            down += clue
        
        html_output = f'<h1 id="title"> {self.title} {self.show_solution*"(Solution)"} </h1>'
        html_output += f'<div id="subtitle">{self.subtitle}</div>'
        for row in html_grid:
            html_output += '<section class="grid-row">' + ''.join(row) + '</section>'

        puzzle_html = html_output + '<br><br>'

        jinja_env = Environment(loader=FileSystemLoader(f'{os.getcwd()}/templates'))
        template = jinja_env.get_template('template_2d.html')
        output = template.render(puzzle=puzzle_html, across=across, down=down)

        if not os.path.exists('output'):
            os.mkdir('output')
            
        with open(f'output/{"_".join(self.title.lower().split(" "))}{self.show_solution*"_solution"}_2d.html', 'w') as f:
            f.write(output)
        print('2D Puzzle created!')
    
    def generate3D(self):
        words = None

        while not words:
            crossword = Cube(self.words, self.scale_factor, max_depth=self.max_depth)
            try:
                words = crossword.generate()
            except(TypeError):
                # TODO: fix cube index issue or check if generation is impossible.
                print('3D puzzle could not be generated.')
            if not words:
                if not self.autogen:
                    print('3D puzzle could not be generated. Trying increasing recursion limit or scale factor.')
                    return None
                print(f'Increasing scale factor to: {self.scale_factor}')
                self.scale_factor += 0.1
        
        length, empty_space, cube = crossword.length, crossword.empty_space, crossword.cube
        guide_cube = self.generate_guide_cube(length, cube, empty_space)

        html_cube = []

        skipped_layers = []
        for z in range(length):
            page = []
            skipped = True
            for y in range(length):
                row = []
                for x in range(length):
                    if guide_cube[z][y][x] == '+':
                        skipped = False
                        row.append('''
                                   <div 
                                        class="row-item" 
                                        style="
                                            background: white;
                                            padding: 5px;
                                            color: white; 
                                            border: 1px solid black">
                                        / 
                                   </div>'''
                                   )
                    else:
                        row.append('''
                                   <div 
                                        class="row-item" 
                                        style="
                                            background: #727272;
                                            padding: 5px; 
                                            color: #727272; 
                                            border: 1px solid black">
                                        / 
                                   </div>'''
                                   )
                page.append(row)
            if skipped:
                skipped_layers.append(z)
            html_cube.append(page)

        across_clues = []
        down_clues = []
        vertical_clues = []
        across = "<br><b>Across</b><br>"
        down = "<br><b>Down</b><br>"
        vertical = "<br><b>Vertical</b><br>"

        numbered_words = self.number_words(words, length, dimension=3)

        for word in numbered_words:
            index = word.index

            if self.show_solution:
                for j,letter in enumerate(word.value):
                    x = word.x + j*word.x_sign
                    y = word.y + j*word.y_sign
                    z = word.z + j*word.z_sign

                    html_cube[z][y][x] = f'''
                        <div 
                            class="row-item"
                            style="
                                background: white;
                                padding: 5px;
                                color: black; 
                                border: 1px solid grey">
                            {letter}
                        </div>'''
            else:
                html_cube[word.z][word.y][word.x] = f'''
                    <div 
                        class="row-item"
                        style="
                            background: white;
                            padding: 5px; 
                            color: black; 
                            border: 1px solid black">
                        {index}
                    </div>'''

            if word.x_sign:
                across_clues.append((index, f'<br>{index}. {self.clues[self.words.index(word.value)]}'))
            elif word.y_sign:
                down_clues.append((index, f'<br>{index}. {self.clues[self.words.index(word.value)]}'))
            else:
                vertical_clues.append((index, f'<br>{index}. {self.clues[self.words.index(word.value)]}'))
                                  
        for (_,clue) in sorted(across_clues, key=lambda x: x[0]):
            across += clue
        for (_,clue) in sorted(down_clues, key=lambda x: x[0]):
            down += clue
        for (_,clue) in sorted(vertical_clues, key=lambda x: x[0]):
            vertical += clue

        html_output = f'<h1 id="title"> {self.title} {self.show_solution*"(Solution)"} </h1>'
        html_output += f'<div id="subtitle">{self.subtitle}</div>'
        layer_number = 0
        for layer,page in enumerate(html_cube):
            if layer in skipped_layers:
                continue
            layer_number += 1
            html_output += f'<h2>Layer {layer_number} </h2>'
            for row in page:
                html_output += '<section class="cube-row">' + ''.join(row) + '</section>'
            html_output += '<br><br><div style="page-break-before: always"<br><br>'

        puzzle_html = html_output + '<br><br>'

        jinja_env = Environment(loader=FileSystemLoader(f'{os.getcwd()}/templates'))
        template = jinja_env.get_template('template_3d.html')
        output = template.render(puzzle=puzzle_html, across=across, down=down, vertical=vertical)

        if not os.path.exists('output'):
            os.mkdir('output')

        with open(f'output/{"_".join(self.title.lower().split(" "))}{self.show_solution*"_solution"}_3d.html', 'w') as f:
            f.write(output)
        print('3D Puzzle created!')
