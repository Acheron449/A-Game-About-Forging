"""Define the guitar equipment item used by the player."""
class Guitar:
    name = "Guitar"
    type = "weapon"
    attack_type = "guitar"

    def __init__(self, attack_animation_frames=None):
        self.attack_animation_frames = attack_animation_frames or []