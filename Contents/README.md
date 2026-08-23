# A-Game-About-Forging
A 2D Pixelated Top Down video game about forging. 

## Internal project map

- `Engine/configuration/constants.py` is the canonical source for shared paths,
	gameplay defaults, input bindings, item identifiers, and resource helpers.
- `Engine/game/` contains stateful gameplay systems: inventory, quests, maps,
	player state, settings, saves, and UI coordination.
- `Engine/main/` contains the running Pygame loop plus legacy rendering and
	bridge adapters used by the prototype runtime.
- `Tests/` contains focused checks for configuration, movement, quests,
	settings, sprite loading, and dependency-update helpers.

## Redundancy note

`Engine/configuration/__init__.py` is marked **REDUNDANT** because its
configuration definitions duplicate the canonical `constants.py` module and
the game imports `constants.py` directly. It remains in the package as a
compatibility artifact until any external imports are removed.

Each Python module contains a short internal docstring describing its role.
