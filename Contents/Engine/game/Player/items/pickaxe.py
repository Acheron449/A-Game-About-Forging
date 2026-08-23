"""Define the pickaxe item and its mining and inventory integration."""
from ...Inventory.item_identifier import create_item


class Pickaxe:

    def __init__(
        self,
        player,
        player_renderer,
        inventory_manager=None,
    ):
        self.player = player
        self.player_renderer = player_renderer
        self.inventory_manager = inventory_manager
        self.is_mining = False

    def mine(self, mining_node):

        if self.is_mining or mining_node.is_depleted:
            return False

        self.is_mining = True

        if not self.player_renderer.start_action("mine"):
            self.is_mining = False
            return False

        reward = mining_node.start_mining(self)

        # A node only awards an item once its health reaches zero.
        if reward is not None:
            resource, amount = reward
            resource_id = str(resource).lower().replace(" ", "_")
            if resource_id.endswith("_ore"):
                resource_id = resource_id[:-4]

            item = create_item(resource_id, quantity=amount)
            if item is None:
                print(f"[Mining] Unknown resource: {resource}")
            elif self.inventory_manager is None:
                print("[Mining] No inventory manager available.")
            elif not self.inventory_manager.move_to_bag(item):
                print("[Mining] Inventory is full; mined item was not added.")
            else:
                print(f"[Mining] Added {amount}x {item.name} to inventory.")

        return True

    def update(self):

        if self.is_mining and self.player_renderer.action is None:
            self.is_mining = False