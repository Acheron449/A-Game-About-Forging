"""Define the gauntlets equipment item used by the player."""
class Gauntlets:
    name = "Gauntlets"
    type = "weapon"
    attack_type = "gauntlets"

    def __init__(self, attack_animation_frames=None):
        self.attack_animation_frames = attack_animation_frames or []