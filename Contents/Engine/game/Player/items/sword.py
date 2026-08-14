class Sword:
    name = "Sword"
    type = "weapon"
    attack_type = "sword"

    def __init__(self, attack_animation_frames=None):
        self.attack_animation_frames = attack_animation_frames or []