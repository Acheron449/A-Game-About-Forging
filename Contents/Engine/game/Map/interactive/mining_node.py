 # Represent a mineable world node and its randomized resource yield.
import random


class MiningNode:

    def __init__(
        self,
        rect,
        possible_resources,
        health=3,
    ):

        self.rect = rect

        self.possible_resources = possible_resources

        self.max_health = health
        self.health = health

        self.is_depleted = False

        self.class_name = "mining_node"

    def can_interact(self, player_rect):
        return self.can_mine(player_rect)

    def can_mine(self, player_rect):

        return (
            self.rect.colliderect(player_rect)
            and not self.is_depleted
        )

    def start_mining(self, pickaxe):

        if self.is_depleted:
            return

        self.health -= 1

        if self.health <= 0:
            return self.break_node()

    def break_node(self):

        self.is_depleted = True

        resource = random.choice(
            self.possible_resources
        )

        amount = random.randint(1, 3)

        print(
            f"Mined {amount}x {resource}"
        )

        return resource, amount