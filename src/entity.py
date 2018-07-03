class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    def __init__(self, x, y, facing, char, color):
        self.x = x
        self.y = y
        self.facing = facing
        self.char = char
        self.color = color

    def move_to(self, x, y, game_map):
        if 0 <= x < game_map.width and 0 <= y < game_map.height and not game_map.get_tile(x, y).blocked:
            self.x = x
            self.y = y
            return True
        return False

    def move(self, dx, dy, game_map):
        return self.move_to(self.x + dx, self.y + dy, game_map)

    # This method and the facing field are temporary, and will be replaced by the ECS
    def face(self, facing):
        self.facing = facing
        return True