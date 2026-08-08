class OreDrop:
    """Represents a type of ore that can drop and its associated weight."""
    def __init__(self, ore_type: str, weight: float):
        self.ore_type = ore_type
        self.weight = weight

class ForgeSystem:
    """
    Forge system framework that uses ores and other materials to create items.
    Requires the ForgeSystem class to be initialized with a list of OreDrop objects,
    which define the types of ores that can be dropped and their weights.
    The system will then randomly select ores based on their weights and use them
    to create items according to the defined recipes.
    """
    def __init__(self, ore_drops: list[OreDrop]):
        self.ore_drops = ore_drops

    def select_ore(self):
        """Randomly selects an ore based on the defined weights."""
        import random
        total_weight = sum(ore.weight for ore in self.ore_drops)
        if total_weight == 0:
            return None

        rand_val = random.uniform(0, total_weight)
        current_sum = 0
        for ore in self.ore_drops:
            current_sum += ore.weight
            if rand_val < current_sum:
                return ore
        return self.ore_drops[0] # Fallback

# Example usage (optional, but helpful for context)
if __name__ == '__main__':
    # Define possible ores and their drop chances (weights)
    possible_ores = [
        OreDrop("Iron Ore", 5.0),
        OreDrop("Gold Ore", 1.0),
        OreDrop("Copper Ore", 10.0)
    ]

    # Initialize the Forge System
    forge = ForgeSystem(possible_ores)

    # Simulate dropping an ore
    dropped_ore = forge.select_ore()
    if dropped_ore:
        print(f"Successfully dropped: {dropped_ore.ore_type}")
