"""mining node behaviour and retrieve resources when mined"""

class MiningNode:

    def __init__(self):

        self.required_tool = "pickaxe"
        self.health = 100

    def interact(self, player):

        attack_controller = player.attack_controller

        successful = attack_controller.use_tool(
            self.required_tool
        )

        if successful:
            self.health -= 10
            print("Mining node hit!")

        if self.health <= 0:
            self.destroy()