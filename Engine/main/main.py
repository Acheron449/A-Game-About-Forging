if __name__ == "__main__":
    from .agaf import Player, Item, Inventory, World

    player = Player(0, 0)
    world = World(player)

    # Example usage
    sword = Item("Sword", "weapon", {"attack": 5}, equippable=True)
    player.inventory.add_item(sword)
    player.inventory.equip(player, sword)

    player.health -= 20
    if player.health <= 0:
        player.die() 