"""bridges the gap between the game logic and the rendering/UI components, ensuring that the game state is accurately represented visually."""
from ..config.config import config
from ..config.imports import * # Import the imports
from .renderer import WorldRenderer, UIRenderer
import pygame # Import pygame for the rectangle

class Player:
    def __init__(self, x, y): # Initialize the player at the given coordinates  
        self.x = x # Set the x coordinate   
        self.y = y # Set the y coordinate   
        self.width = config.PLAYER_HITBOX_WIDTH # Set the width of the hitbox
        self.height = config.PLAYER_HITBOX_HEIGHT # Set the height of the hitbox
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height) # Create a rectangle for the player
        self.health = config.PLAYER_START_HEALTH # Set the starting health
        self.max_health = config.PLAYER_START_MAX_HEALTH # Set the maximum health
        self.mana = config.PLAYER_START_MANA # Set the starting mana
        self.max_mana = config.PLAYER_START_MAX_MANA # Set the maximum mana
        self.stamina = config.PLAYER_START_STAMINA # Set the starting stamina
        self.max_stamina = config.PLAYER_START_MAX_STAMINA # Set the maximum stamina
        self.xp = config.PLAYER_START_XP # Set the starting xp
        self.level = config.PLAYER_START_LEVEL # Set the starting level
        self.gold = config.PLAYER_START_GOLD # Set the starting gold
        self.stats = dict(config.PLAYER_START_STATS) # Set the starting stats
        self.equipped_items = {'weapon': None, 'armor': None, 'helmet': None, 'boots': None} # Set the starting equipped items
        self.inventory = Inventory() # Create an inventory for the player
        self.appearance = config.DEFAULT_PLAYER_APPEARANCE # Set the starting appearance
        self.pickaxe_equipped = False # Set the starting pickaxe equipped

    def update_rect(self): # Update the rectangle
        self.rect.topleft = (self.x, self.y) # Update the rectangle to the new coordinates      

    def move(self, dx, dy, world=None): # Move the player by the given amount
        new_rect = self.rect.move(dx, dy) # Move the rectangle by the given amount  
        if world is None or world.can_move_rect(new_rect): # Check if the player can move to the new position   
            self.x += dx # Add the x coordinate to the player
            self.y += dy # Add the y coordinate to the player                       
            self.update_rect() # Update the rectangle to the new coordinates
            return True # Return True if the player can move to the new position
        return False # Return False if the player cannot move to the new position

    def attack(self, enemy): # Attack an enemy
        damage = self.stats['strength'] # Get the strength of the player
        enemy.take_damage(damage) # Take damage from the enemy

    def take_damage(self, damage): # Take damage from the player
        actual_damage = max(0, damage - self.stats['defense']) # Calculate the actual damage
        self.health -= actual_damage # Subtract the actual damage from the health
        if self.health <= 0: # Check if the player is dead
            self.die() # Die

    def collect_item(self, item): # Collect an item
        self.inventory.add_item(item) # Add the item to the inventory
        if item.type == 'gold':
            self.gold += item.value # Add the value of the item to the gold
        elif item.type == 'xp':
            self.gain_xp(item.value) # Add the value of the item to the xp

    def mine(self, world, mouse_buttons): # Mine a nearby mining spot when left mouse is pressed
        """Attempt to mine a nearby mining spot when left mouse is pressed."""
        weapon = self.equipped_items.get('weapon') # Get the weapon from the equipped items
        if not weapon or weapon.name.lower() != config.PICKAXE_NAME_KEY: # Check if the weapon is not equipped or the name is not the pickaxe name
            return None # Return None if the weapon is not equipped or the name is not the pickaxe name

        if not mouse_buttons or not mouse_buttons[0]: # Check if the left mouse button is not pressed
            return None # Return None if the left mouse button is not pressed

        for entity in list(world.entities):
            if isinstance(entity, MiningSpot) and self.rect.colliderect(entity.rect): # Check if the entity is a mining spot and the player is colliding with the mining spot   
                item = entity.mine() # Mine the mining spot
                if item: # Check if the item is not None
                    self.collect_item(item) # Collect the item
                    world.entities.remove(entity) # Remove the mining spot from the world
                    return item # Return the item
        return None # Return None if the item is None

    def equipped_weapon(self):
        """Return the currently equipped weapon item, if any."""
        return self.equipped_items.get('weapon')

    def equipped_weapon_type(self):
        """Return the normalized weapon animation type for the currently equipped weapon."""
        weapon = self.equipped_weapon()
        if weapon is None:
            return None
        animation_type = getattr(weapon, 'animation_type', None)
        if isinstance(animation_type, str) and animation_type:
            return animation_type.lower()
        name = getattr(weapon, 'name', '').lower()
        if 'pickaxe' in name:
            return 'pickaxe'
        if 'greatsword' in name:
            return 'greatsword'
        if 'sword' in name:
            return 'sword'
        if getattr(weapon, 'type', '').lower() == 'weapon':
            return 'sword'
        return None

    def gain_xp(self, amount): # Gain xp from the player
        self.xp += amount
        if self.xp >= self.level * config.XP_PER_LEVEL_MULTIPLIER: # Check if the xp is greater than or equal to the level times the xp per level multiplier
            self.level_up() # Level up the player

    def level_up(self): # Level up the player
        self.level += 1
        self.max_health += config.LEVEL_UP_MAX_HEALTH_BONUS # Add the level up max health bonus to the maximum health
        self.health = self.max_health # Set the health to the maximum health
        # Allocate points to upgrade tree

    def equip_item(self, item): # Equip an item
        if item.equippable and item.type in self.equipped_items:
            old_item = self.equipped_items[item.type] # Get the old item from the equipped items
            if old_item: # Check if the old item is not None
                self.unequip_item(old_item) # Unequip the old item
            self.equipped_items[item.type] = item # Equip the item
            for stat, bonus in item.stats_bonus.items(): # Add the stats bonus to the stats
                self.stats[stat] += bonus # Add the stats bonus to the stats
            if item.name.lower() == config.PICKAXE_NAME_KEY: # Check if the item name is the pickaxe name
                self.pickaxe_equipped = True # Set the pickaxe equipped to True

    def unequip_item(self, item): # Unequip an item
        if self.equipped_items[item.type] == item:
            self.equipped_items[item.type] = None # Set the equipped item to None
            for stat, bonus in item.stats_bonus.items(): # Subtract the stats bonus from the stats
                self.stats[stat] -= bonus # Subtract the stats bonus from the stats
            if item.name.lower() == config.PICKAXE_NAME_KEY: # Check if the item name is the pickaxe name
                self.pickaxe_equipped = False # Set the pickaxe equipped to False

    def die(self): # Die
        # Handle death
        pass # Do nothing

class Item:
    def __init__(self, name, item_type, stats_bonus=None, equippable=False, value=0, animation_type=None): # Initialize an item
        self.name = name # Set the name of the item
        self.type = item_type  # 'weapon', 'armor', etc., or 'gold', 'xp'
        self.stats_bonus = stats_bonus or {} # Set the stats bonus to the stats bonus
        self.equippable = equippable # Set the equippable to the equippable
        self.value = value # Set the value of the item
        self.animation_type = animation_type # Set the animation type for equipped weapon/tool

class Inventory:
    def __init__(self): # Initialize an inventory
        self.items = [] # Set the items to the items

    def add_item(self, item): # Add an item to the inventory
        self.items.append(item)

    def remove_item(self, item): # Remove an item from the inventory
        if item in self.items:
            self.items.remove(item) # Remove the item from the inventory

    def equip(self, player, item): # Equip an item
        if item in self.items:
            player.equip_item(item) # Equip the item
            self.remove_item(item) # Remove the item from the inventory

    def unequip(self, player, item_type): # Unequip an item
        item = player.equipped_items[item_type] # Get the item from the equipped items
        if item: # Check if the item is not None
            player.unequip_item(item) # Unequip the item
            self.add_item(item) # Add the item to the inventory

class World:
    def __init__(self, player, tile_size=config.WORLD_DEFAULT_TILE_SIZE): # Initialize a world
        self.player = player # Set the player to the player in the world
        self.entities = []  # List of enemies, collectables, etc.
        self.map = []  # Simple 2D list for map
        self.tile_size = tile_size # Set the tile size to the tile size
        self.renderer = WorldRenderer() # Set the renderer to the world renderer

    def set_map(self, tile_grid): # Set the map to the tile grid
        self.map = tile_grid # Set the map to the tile grid

    def tile_at(self, tile_x, tile_y): # Get the tile at the given coordinates
        if tile_y < 0 or tile_x < 0 or tile_y >= len(self.map) or tile_x >= len(self.map[0]): # Check if the tile is out of bounds
            return 1 # Return 1 if the tile is out of bounds
        return self.map[tile_y][tile_x] # Return the tile at the given coordinates

    def is_walkable_tile(self, tile_x, tile_y): # Check if the tile is walkable
        return self.tile_at(tile_x, tile_y) == 0 # Return True if the tile is walkable, False otherwise     

    def can_move_rect(self, rect): # Check if the rectangle can move to the given position
        if not self.map:
            return True
        corners = [
            (rect.left, rect.top),
            (rect.right - 1, rect.top),
            (rect.left, rect.bottom - 1),
            (rect.right - 1, rect.bottom - 1),
        ]
        for px, py in corners: # Check if the rectangle is on a walkable tile
            tile_x = px // self.tile_size # Get the tile x coordinate
            tile_y = py // self.tile_size # Get the tile y coordinate
            if not self.is_walkable_tile(tile_x, tile_y): # Check if the tile is not walkable
                return False # If the tile is not walkable, return False
        return True # If the tile is walkable, return True

    def render(self, screen): # Render the world
        self.renderer.render_world(self, screen) # Render the world

    def update(self): # Update the world
        # Update entities
        pass

    def spawn_collectable(self, x, y, item): # Spawn a collectable at the given coordinates
        self.entities.append(Collectable(x, y, item))

    def spawn_mining_spot(self, x, y, item=None): # Spawn a mining spot at the given coordinates
        self.entities.append(MiningSpot(x, y, item))

    def interact(self, entity, player, mouse_buttons=None): # Interact with an entity with the left mouse button
        if isinstance(entity, MiningSpot) and player.rect.colliderect(entity.rect) and mouse_buttons and mouse_buttons[0]:
            mined_item = entity.mine() # Mine the mining spot
            if mined_item:
                player.collect_item(mined_item) # Collect the item
                self.entities.remove(entity) # Remove the mining spot from the world
                return mined_item # Return the mined item
        return None

class Collectable:
    def __init__(self, x, y, item): # Initialize a collectable
        self.x = x
        self.y = y
        self.item = item # Set the item to the item

class MiningSpot:
    def __init__(self, x, y, item=None): # Initialize a mining spot
        self.x = x
        self.y = y
        self.width = config.MINING_SPOT_WIDTH # Set the width of the mining spot
        self.height = config.MINING_SPOT_HEIGHT # Set the height of the mining spot
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.item = item or Item(
            config.DEFAULT_MINING_ITEM_NAME,
            config.DEFAULT_MINING_ITEM_TYPE,
            value=config.DEFAULT_MINING_ITEM_VALUE,
        )
        self.mined = False # Set the mined to the mined

    def mine(self): # Mine the mining spot
        if self.mined:
            return None # Return None if the mining spot is already mined
        self.mined = True # Set the mined to the mined
        return self.item # Return the item  

class Enemy:
    def __init__(self, x, y, health, damage): # Initialize an enemy
        self.x = x
        self.y = y
        self.health = health # Set the health to the health
        self.damage = damage # Set the damage to the damage

    def take_damage(self, damage): # Take damage from the enemy
        self.health -= damage # Subtract the damage from the health
        if self.health <= 0: # Check if the health is less than or equal to 0
            self.die() # Die

    def die(self): # Die    
        # Drop loot
        pass # Do nothing

class UpgradeTree:
    def __init__(self, player): # Initialize an upgrade tree
        self.player = player # Set the player to the player in the upgrade tree
        self.available_upgrades = dict(UPGRADE_TREE_INITIAL_COUNTS) # Set the available upgrades to the available upgrades

    def apply_upgrade(self, stat): # Apply an upgrade to the player
        if self.available_upgrades[stat] > 0: # Check if the available upgrades is greater than 0
            self.player.stats[stat] += 1 # Add 1 to the stat
            self.available_upgrades[stat] -= 1 # Subtract 1 from the available upgrades

class UI:
    def __init__(self, player): # Initialize a UI
        self.player = player # Set the player to the player in the UI
        self.renderer = UIRenderer(player) # Set the renderer to the UI renderer

    def draw(self, screen): # Draw the UI
        self.renderer.draw_ui(screen) # Draw the UI

    def update(self): # Update the UI
        self.renderer.update_ui() # Update the UI

    def configure_appearance(self, appearance): # Configure the appearance of the UI
        self.renderer.configure_appearance(appearance) # Configure the appearance of the UI

# Main game class
class Game:
    def __init__(self): # Initialize a game
        self.player = Player(0, 0) # Set the player to the player in the game
        self.world = World(self.player) # Set the world to the world in the game
        self.ui = UI(self.player) # Set the UI to the UI in the game
        self.upgrade_tree = UpgradeTree(self.player) # Set the upgrade tree to the upgrade tree in the game

    def run(self): # Run the game
        # Main game loop
        pass # Do nothing

