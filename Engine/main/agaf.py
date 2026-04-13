from ..config.config import *
from ..config.imports import *
from .renderer import WorldRenderer, UIRenderer
import pygame

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.health = 100
        self.max_health = 100
        self.mana = 50
        self.max_mana = 50
        self.xp = 0
        self.level = 1
        self.gold = 0
        self.stats = {'strength': 10, 'defense': 5, 'speed': 5}
        self.equipped_items = {'weapon': None, 'armor': None, 'helmet': None, 'boots': None}
        self.inventory = Inventory()
        self.appearance = 'default'  # Can be configured
        self.pickaxe_equipped = False

    def update_rect(self):
        self.rect.topleft = (self.x, self.y)

    def move(self, dx, dy, world=None):
        new_rect = self.rect.move(dx, dy)
        if world is None or world.can_move_rect(new_rect):
            self.x += dx
            self.y += dy
            self.update_rect()
            return True
        return False

    def attack(self, enemy):
        damage = self.stats['strength']
        enemy.take_damage(damage)

    def take_damage(self, damage):
        actual_damage = max(0, damage - self.stats['defense'])
        self.health -= actual_damage
        if self.health <= 0:
            self.die()

    def collect_item(self, item):
        self.inventory.add_item(item)
        if item.type == 'gold':
            self.gold += item.value
        elif item.type == 'xp':
            self.gain_xp(item.value)

    def mine(self, world, mouse_buttons):
        """Attempt to mine a nearby mining spot when left mouse is pressed."""
        weapon = self.equipped_items.get('weapon')
        if not weapon or weapon.name.lower() != 'pickaxe':
            return None

        if not mouse_buttons or not mouse_buttons[0]:
            return None

        for entity in list(world.entities):
            if isinstance(entity, MiningSpot) and self.rect.colliderect(entity.rect):
                item = entity.mine()
                if item:
                    self.collect_item(item)
                    world.entities.remove(entity)
                    return item
        return None

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.level * 100:  # Simple leveling
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_health += 10
        self.health = self.max_health
        # Allocate points to upgrade tree

    def equip_item(self, item):
        if item.equippable and item.type in self.equipped_items:
            old_item = self.equipped_items[item.type]
            if old_item:
                self.unequip_item(old_item)
            self.equipped_items[item.type] = item
            for stat, bonus in item.stats_bonus.items():
                self.stats[stat] += bonus
            if item.name.lower() == 'pickaxe':
                self.pickaxe_equipped = True

    def unequip_item(self, item):
        if self.equipped_items[item.type] == item:
            self.equipped_items[item.type] = None
            for stat, bonus in item.stats_bonus.items():
                self.stats[stat] -= bonus
            if item.name.lower() == 'pickaxe':
                self.pickaxe_equipped = False

    def die(self):
        # Handle death
        pass

class Item:
    def __init__(self, name, item_type, stats_bonus=None, equippable=False, value=0):
        self.name = name
        self.type = item_type  # 'weapon', 'armor', etc., or 'gold', 'xp'
        self.stats_bonus = stats_bonus or {}
        self.equippable = equippable
        self.value = value

class Inventory:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):# Remove item from inventory
        if item in self.items:
            self.items.remove(item) # Remove item from inventory

    def equip(self, player, item):
        if item in self.items:
            player.equip_item(item)
            self.remove_item(item)

    def unequip(self, player, item_type):
        item = player.equipped_items[item_type]
        if item:
            player.unequip_item(item)
            self.add_item(item)

class World:
    def __init__(self, player, tile_size=16):
        self.player = player
        self.entities = []  # List of enemies, collectables, etc.
        self.map = []  # Simple 2D list for map
        self.tile_size = tile_size
        self.renderer = WorldRenderer()

    def set_map(self, tile_grid):
        self.map = tile_grid

    def tile_at(self, tile_x, tile_y):
        if tile_y < 0 or tile_x < 0 or tile_y >= len(self.map) or tile_x >= len(self.map[0]):
            return 1
        return self.map[tile_y][tile_x]

    def is_walkable_tile(self, tile_x, tile_y):
        return self.tile_at(tile_x, tile_y) == 0

    def can_move_rect(self, rect):
        if not self.map:
            return True
        corners = [
            (rect.left, rect.top),
            (rect.right - 1, rect.top),
            (rect.left, rect.bottom - 1),
            (rect.right - 1, rect.bottom - 1),
        ]
        for px, py in corners:
            tile_x = px // self.tile_size
            tile_y = py // self.tile_size
            if not self.is_walkable_tile(tile_x, tile_y):
                return False
        return True

    def render(self, screen):
        self.renderer.render_world(self, screen)

    def update(self):
        # Update entities
        pass

    def spawn_collectable(self, x, y, item):
        self.entities.append(Collectable(x, y, item))

    def spawn_mining_spot(self, x, y, item=None):
        self.entities.append(MiningSpot(x, y, item))

    def interact(self, entity, player, mouse_buttons=None):
        if isinstance(entity, MiningSpot) and player.rect.colliderect(entity.rect) and mouse_buttons and mouse_buttons[0]:
            mined_item = entity.mine()
            if mined_item:
                player.collect_item(mined_item)
                self.entities.remove(entity)
                return mined_item
        return None

class Collectable:
    def __init__(self, x, y, item):
        self.x = x
        self.y = y
        self.item = item

class MiningSpot:
    def __init__(self, x, y, item=None):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.item = item or Item('Stone Ore', 'ore', value=1)
        self.mined = False

    def mine(self):
        if self.mined:
            return None
        self.mined = True
        return self.item

class Enemy:
    def __init__(self, x, y, health, damage):
        self.x = x
        self.y = y
        self.health = health
        self.damage = damage

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.die()

    def die(self):
        # Drop loot
        pass

class UpgradeTree:
    def __init__(self, player):
        self.player = player
        self.available_upgrades = {'strength': 0, 'defense': 0, 'speed': 0}

    def apply_upgrade(self, stat):
        if self.available_upgrades[stat] > 0:
            self.player.stats[stat] += 1
            self.available_upgrades[stat] -= 1

class UI:
    def __init__(self, player):
        self.player = player
        self.renderer = UIRenderer(player)

    def draw(self, screen):
        self.renderer.draw_ui(screen)

    def update(self):
        self.renderer.update_ui()

    def configure_appearance(self, appearance):
        self.renderer.configure_appearance(appearance)

# Main game class
class Game:
    def __init__(self):
        self.player = Player(0, 0)
        self.world = World(self.player)
        self.ui = UI(self.player)
        self.upgrade_tree = UpgradeTree(self.player)

    def run(self):
        # Main game loop
        pass

