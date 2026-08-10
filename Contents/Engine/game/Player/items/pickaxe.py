class Pickaxe:
    name = "Pickaxe"
    type = "tool"
    attack_type = "pickaxe"

    def __init__(self, attack_animation_frames=None):
        self.attack_animation_frames = attack_animation_frames or []