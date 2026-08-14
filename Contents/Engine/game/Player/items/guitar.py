class Guitar:
    name = "Guitar"
    type = "weapon"
    attack_type = "guitar"

    def __init__(self, attack_animation_frames=None):
        self.attack_animation_frames = attack_animation_frames or []