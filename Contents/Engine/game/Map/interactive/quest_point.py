import pygame


class QuestPoint:
    """
    Tiled-defined interaction point that executes a sequence of actions.

    Tiled properties can include:

        class: quest_point
        sequence: door, complete_quest
        prerequisite: pickaxe
        target_map: tutorial
        spawn_id: cave_exit
        quest_id: tutorial_cave
    """

    def __init__(
        self,
        x,
        y,
        width,
        height,
        properties=None,
    ):
        self.rect = pygame.Rect(
            x,
            y,
            width,
            height,
        )

        self.properties = properties or {}

        # QUEST CONFIGURATION

        self.sequence = str(
            self.properties.get("sequence", "")
        )

        self.prerequisite = str(
            self.properties.get("prerequisite", "none")
        )

        self.target_map = self.properties.get(
            "target_map"
        )

        self.spawn_id = self.properties.get(
            "spawn_id"
        )

        self.quest_id = self.properties.get(
            "quest_id"
        )

        # quest_point.py — inside __init__
        self.class_name = "quest_point"
        
        # STATE

        self.active = True
        self.running = False
        self.current_step = 0

        self.steps = self._build_steps()

    # SEQUENCE

    def _build_steps(self):
        if not self.sequence:
            return []

        return [
            step.strip().lower()
            for step in self.sequence.split(",")
            if step.strip()
        ]

    # PREREQUISITES

    def prerequisite_met(self, play_state):

        prerequisite = self.prerequisite.strip().lower()

        if prerequisite in ("", "none"):
            return True

        if prerequisite == "pickaxe":

            hotbar_ui = play_state.get(
                "hotbar_ui"
            )

            if hotbar_ui is None:
                return False

            # This is the item in the currently selected hotbar slot.
            equipped = hotbar_ui.get_selected_item()

            if equipped is None:
                return False

            equipped_item_type = str(
                getattr(equipped, "item_type", "")
            ).lower()

            equipped_name = str(
                getattr(equipped, "name", "")
            ).lower()

            return (
                "pickaxe" in equipped_item_type
                or "pickaxe" in equipped_name
            )
        
        print(
            f"[QuestPoint] Unknown prerequisite: "
            f"{prerequisite}"
        )

        return False


    def can_interact(self, player_rect):
        return (
            self.active
            and self.rect.colliderect(player_rect)
        )

    # TRIGGER

    def trigger(self, play_state):

        if not self.active:
            return

        if self.running:
            return

        if not self.prerequisite_met(play_state):

            print(
                "[QuestPoint] Prerequisite not met:",
                self.prerequisite,
            )

            return

        if not self.steps:

            print(
                "[QuestPoint] No sequence defined."
            )

            return

        self.running = True
        self.current_step = 0

        print(
            "[QuestPoint] Starting sequence:",
            self.steps,
        )

        self._run_next_step(play_state)

    # STEP PROCESSING

    def _run_next_step(self, play_state):

        if self.current_step >= len(self.steps):

            self.running = False
            self.active = False

            print(
                "[QuestPoint] Sequence complete."
            )

            return

        step = self.steps[
            self.current_step
        ]

        print(
            "[QuestPoint] Running step:",
            step,
        )

        # DOOR

        if step == "door":
            self._door(play_state)

        # QUEST COMPLETION

        elif step == "complete_quest":

            self.complete_quest(
                play_state
            )

        # UNKNOWN

        else:

            print(
                f"[QuestPoint] Unknown step: {step}"
            )

            self._step_complete(
                play_state
            )

    # DOOR

    def _door(self, play_state):

        if not self.target_map:

            print(
                "[QuestPoint] No target_map specified."
            )

            self._step_complete(
                play_state
            )

            return

        if not self.spawn_id:

            print(
                "[QuestPoint] No spawn_id specified."
            )

            self._step_complete(
                play_state
            )

            return

        print(
            f"[QuestPoint] Door -> "
            f"{self.target_map} "
            f"spawn={self.spawn_id}"
        )

        # Tell main.py that a map transition is required.

        play_state[
            "pending_map_transition"
        ] = {
            "target_map": self.target_map,
            "spawn_id": self.spawn_id,
            "quest_point": self,
        }

        # Do NOT complete the step yet.
        #
        # main.py will perform the transition and then
        # call step_complete().

    # QUEST COMPLETION

    def complete_quest(self, play_state):

        quest_manager = play_state.get(
            "quest_manager"
        )

        if quest_manager is None:

            print(
                "[QuestPoint] QuestManager not found."
            )

            self._step_complete(
                play_state
            )

            return

        if self.quest_id:

            quest_manager.mark_completed(
                self.quest_id
            )

            print(
                f"[QuestPoint] Completed quest: "
                f"{self.quest_id}"
            )

        self._step_complete(
            play_state
        )

    # STEP COMPLETE

    def _step_complete(self, play_state):

        self.current_step += 1

        self._run_next_step(
            play_state
        )
