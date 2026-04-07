from ..config.config import *
from ..config.imports import *
from .renderer import WorldRenderer, UIRenderer

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 100
        self.max_health = 100
        self.xp = 0
        self.level = 1
        self.gold = 0
        self.stats = {'strength': 10, 'defense': 5, 'speed': 5}
        self.equipped_items = {'weapon': None, 'armor': None, 'helmet': None, 'boots': None}
        self.inventory = Inventory()
        self.appearance = 'default'  # Can be configured

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

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

    def unequip_item(self, item):
        if self.equipped_items[item.type] == item:
            self.equipped_items[item.type] = None
            for stat, bonus in item.stats_bonus.items():
                self.stats[stat] -= bonus

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

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)

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
    def __init__(self, player):
        self.player = player
        self.entities = []  # List of enemies, collectables, etc.
        self.map = []  # Simple 2D list for map
        self.renderer = WorldRenderer()

    def render(self, screen):
        self.renderer.render_world(self, screen)

    def update(self):
        # Update entities
        pass

    def spawn_collectable(self, x, y, item):
        self.entities.append(Collectable(x, y, item))

    def spawn_mining_spot(self, x, y):
        self.entities.append(MiningSpot(x, y))

    def interact(self, entity):
        # Handle interaction
        pass

class Collectable:
    def __init__(self, x, y, item):
        self.x = x
        self.y = y
        self.item = item

class MiningSpot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

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

