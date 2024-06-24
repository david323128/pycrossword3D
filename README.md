# pycrossword3D
Generates a printable 2D or 3D crossword puzzle using `jinja2`. The 3D puzzle is just a series of 2D crossword layers starting from the top of the cube.


## To Run

### Install Dependency
`pip install jinja2`

### Configure
Add puzzle data to `data.json` and change `puzzle_name` in `example.py`. Then run:

`python example.py`

You can optionally increase `max_depth` or change `scale_factor` to adjust the puzzle size.


## Algorithm
The search starts by inserting the longest word(pivot word) somewhere in the middle of the grid, and then inserts the remaining words sorted by length. Each word object records all previous positions and orientations in a set to prevent repeating arrangements. If an insertion fails the previous word is removed and remaining words are reinserted at new positions unless `max_depth` is exceeded, at which point the grid is reset.

Before a word is inserted it is checked for a common letter in an inserted word, and rotated if it has the same orientation. Then the surrounding squares are checked at the same time by multiplying the relative position by the orientation which just simplifies the indexing. If there are adjacent letters that form the beginning of other words, those words are all checked and inserted if possible.

The insertion check for the cube works the same except for the additional direction that has to be checked for adjacent words.

