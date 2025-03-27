import pygame
import os
import random
from entities.tile import Tile
from config import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT

class MapManager:
    def __init__(self):
        self.tiles = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.tileset = {}
        self.load_tileset()
    
    def load_tileset(self):
        """Load and scale all tileset images."""
        # Load all necessary tiles
        tileset_path = os.path.join('assets', 'TILESET VILLAGE TOP DOWN')
        
        # Scale factor for tiles
        SCALE = 2.0
        
        def load_and_scale(filename):
            """Helper to load and scale a tile image."""
            try:
                img = pygame.image.load(os.path.join(tileset_path, filename)).convert_alpha()
                return pygame.transform.scale(img, 
                    (int(TILE_SIZE * SCALE), 
                     int(TILE_SIZE * SCALE)))
            except pygame.error:
                # Create a colored rectangle as fallback
                surface = pygame.Surface((TILE_SIZE * SCALE, TILE_SIZE * SCALE))
                surface.fill((100, 200, 100))  # Light green for grass
                return surface
        
        # Load grass variations for more natural looking ground
        self.tileset = {
            'grass': load_and_scale('GRASS TILE - DAY.png'),
            'grass_detail1': load_and_scale('GRASS DETAIL 1 - DAY.png'),
            'grass_detail2': load_and_scale('GRASS DETAIL 3 - DAY.png'),
            'grass_detail3': load_and_scale('GRASS DETAIL 4 - DAY.png'),
            'grass_detail4': load_and_scale('GRASS DETAIL 5 - DAY.png'),
            'grass_detail5': load_and_scale('GRASS DETAIL 6 - DAY.png'),
            'ground': load_and_scale('GROUND TILE - DAY.png'),
            'house1': load_and_scale('HOUSE 1 - DAY.png'),
            'house2': load_and_scale('HOUSE 2 - DAY.png'),
            'tree1': load_and_scale('TREE 2 - DAY.png'),
            'tree2': load_and_scale('TREE 3 - DAY.png'),
            'fence': load_and_scale('FENCE 1 - DAY.png'),
            'water': load_and_scale('WATER TILE - DAY.png'),
            'bridge': load_and_scale('BRIDGE - DAY.png'),
            'church': load_and_scale('CHURCH - DAY.png'),
        }

    def generate_map(self):
        """Generate the game map with grass variations and decorative elements."""
        # Clear existing tiles
        self.tiles.empty()
        self.walls.empty()
        
        # Get tile size from a grass tile
        tile_size = self.tileset['grass'].get_width()
        
        # Base layer - grass with variations
        for y in range(0, MAP_HEIGHT, tile_size):
            for x in range(0, MAP_WIDTH, tile_size):
                # Randomly choose between grass variations
                if random.random() < 0.7:  # 70% chance of basic grass
                    grass = Tile(x, y, self.tileset['grass'])
                else:
                    # Choose a random grass detail
                    detail_type = random.choice([
                        'grass_detail1', 'grass_detail2', 'grass_detail3',
                        'grass_detail4', 'grass_detail5'
                    ])
                    grass = Tile(x, y, self.tileset[detail_type])
                self.tiles.add(grass)
        
        # Add paths and decorative elements
        self.add_paths()
        self.add_buildings()
        self.add_trees()
        
        return self.tiles, self.walls
    
    def add_paths(self):
        """Add dirt paths through the map."""
        tile_size = self.tileset['ground'].get_width()
        
        # Create a main path from left to right
        y = MAP_HEIGHT // 2 - tile_size // 2
        for x in range(0, MAP_WIDTH, tile_size):
            ground = Tile(x, y, self.tileset['ground'])
            self.tiles.add(ground)
        
        # Create a crossing path from top to bottom
        x = MAP_WIDTH // 2 - tile_size // 2
        for y in range(0, MAP_HEIGHT, tile_size):
            ground = Tile(x, y, self.tileset['ground'])
            self.tiles.add(ground)
    
    def add_buildings(self):
        """Add buildings and create collision walls."""
        tile_size = self.tileset['house1'].get_width()
        
        # Add houses at specific positions
        house_positions = [
            (MAP_WIDTH // 4, MAP_HEIGHT // 4),
            (MAP_WIDTH * 3 // 4, MAP_HEIGHT // 4),
            (MAP_WIDTH // 4, MAP_HEIGHT * 3 // 4),
            (MAP_WIDTH * 3 // 4, MAP_HEIGHT * 3 // 4),
        ]
        
        for x, y in house_positions:
            house = Tile(x - tile_size // 2, y - tile_size // 2, self.tileset['house1'], is_wall=True)
            self.tiles.add(house)
            self.walls.add(house)
        
        # Add church in center
        church_size = self.tileset['church'].get_width()
        church = Tile(
            MAP_WIDTH // 2 - church_size // 2,
            MAP_HEIGHT // 2 - church_size // 2,
            self.tileset['church'],
            is_wall=True
        )
        self.tiles.add(church)
        self.walls.add(church)
    
    def add_trees(self):
        """Add trees around the map edges."""
        tile_size = self.tileset['tree1'].get_width()
        spacing = tile_size * 2
        
        # Add trees along edges with random variation
        for i in range(0, MAP_WIDTH, spacing):
            if random.random() < 0.7:  # 70% chance to place a tree
                # Top edge
                tree = Tile(i, spacing, self.tileset['tree1'], is_wall=True)
                self.tiles.add(tree)
                self.walls.add(tree)
                
                # Bottom edge
                tree = Tile(i, MAP_HEIGHT - spacing * 2, self.tileset['tree2'], is_wall=True)
                self.tiles.add(tree)
                self.walls.add(tree)
        
        for i in range(0, MAP_HEIGHT, spacing):
            if random.random() < 0.7:
                # Left edge
                tree = Tile(spacing, i, random.choice([self.tileset['tree1'], self.tileset['tree2']]), is_wall=True)
                self.tiles.add(tree)
                self.walls.add(tree)
                
                # Right edge
                tree = Tile(MAP_WIDTH - spacing * 2, i, random.choice([self.tileset['tree1'], self.tileset['tree2']]), is_wall=True)
                self.tiles.add(tree)
                self.walls.add(tree)
