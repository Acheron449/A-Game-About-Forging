class Pickaxe:

    def __init__(self, player, player_renderer):
        self.player = player
        self.player_renderer = player_renderer

        self.is_mining = False

    def mine(self, mining_node):

        if self.is_mining:
            return False

        if mining_node.is_depleted:
            return False

        self.is_mining = True

        started = self.player_renderer.start_action(
            "mine"
        )

        if not started:
            self.is_mining = False
            return False

        mining_node.start_mining(self)

        return True

    def update(self):

        if not self.is_mining:
            return

        if self.player_renderer.action is None:

            self.is_mining = False