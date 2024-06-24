class Word2D:
    def __init__(self, value, index, x = None, y = None):
        self.value = value
        self.length = len(value)
        self.x_sign = 1
        self.y_sign = 0
        self.index = index
        self.insertion_history = set()
        self.x = x
        self.y = y

    def clear_insertion_history(self):
        self.insertion_history = set()

    def generate_insertion_entry(self):
        return f'{self.x}-{self.y}-{self.x_sign}'

    def add_insertion_entry(self, insertion):
        self.insertion_history.add(insertion)

    def update_position(self, x, y):
        self.x = x
        self.y = y

    def clear_position(self):
        self.x = None
        self.y = None

    def get_orientation(self):
        return (self.x_sign, self.y_sign)

    def rotate(self):
        self.x_sign ^= 1
        self.y_sign ^= 1


class Word3D:
    def __init__(self, value, index, x = None, y = None, z = None):
        self.value = value
        self.length = len(value)
        self.x_sign = 0
        self.y_sign = 0
        self.z_sign = 1
        self.index = index
        self.insertion_history = set()
        self.x = x
        self.y = y
        self.z = z

    def clear_insertion_history(self):
        self.insertion_history.clear()

    def generate_insertion_entry(self):
        return f'{self.x}-{self.y}-{self.z}-{self.x_sign}-{self.y_sign}-{self.z_sign}'

    def add_insertion_entry(self, insertion):
        self.insertion_history.add(insertion)

    def update_position(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def clear_position(self):
        self.x = None
        self.y = None
        self.z = None

    def get_orientation(self):
        return (self.x_sign, self.y_sign, self.z_sign)

    def rotate(self):
        x_sign, y_sign, z_sign = self.x_sign, self.y_sign, self.z_sign
        self.x_sign = z_sign
        self.y_sign = x_sign
        self.z_sign = y_sign