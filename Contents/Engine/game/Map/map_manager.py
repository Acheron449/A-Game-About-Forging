
from __future__ import annotations
from pathlib import Path
from typing import Optional
from ...configuration.constants import config
from ...configuration.imports import pg

from .map_loader import TiledMap


class MapManager:

    def __init__(self, maps_directory: Path, scale: float = 1.0):
        self.maps_directory = Path(maps_directory)
        self.scale = scale

        self.current_map: Optional[TiledMap] = None
        self.current_map_name: Optional[str] = None

        self.spawn_position = (0, 0)

        self.camera_x = 0
        self.camera_y = 0




    def load_map(self, map_name: str, spawn_id="default"):
        """
        Load a map from the maps directory.

        Example:
            load_map("cave", spawn_position=(300, 300))
        """

        map_path = self.maps_directory / f"{map_name}.tmx"

        print("MAP DIRECTORY:", self.maps_directory)
        print("MAPS FOUND:")

        for file in self.maps_directory.glob("*.tmx"):
            print("  ", file.name)

        print(f"Loading map: {map_path}")

        if not map_path.exists():
            raise FileNotFoundError(
                f"Map does not exist: {map_path}"
            )

        # pytmx loading
        import pytmx

        tmx_data = pytmx.load_pygame(
            str(map_path),
            pixelalpha=True
        )

        self.current_map = TiledMap(
            tmx_data,
            map_path.parent,
            scale=self.scale
        )

        self.current_map_name = map_name
        self.spawn_position = self.current_map.get_spawn_position(spawn_id)

        # Reset camera
        self.camera_x = 0
        self.camera_y = 0

        print(f"Map '{map_name}' loaded successfully.")

    @property
    def collision_objects(self):
        if self.current_map is None:
            return []

        return self.current_map.collision_objects

    @property
    def current_map_data(self):
        return self.current_map

    def set_camera(self, x, y):
        self.camera_x = x
        self.camera_y = y

    @property
    def camera_position(self):
        return self.camera_x, self.camera_y

class TiledCollisionObject:

    def __init__(self, obj_data):
        self.id = obj_data.id

        self.x = obj_data.x
        self.y = obj_data.y

        self.points = []

        if hasattr(obj_data, "polygon") and obj_data.polygon:

            for pt in obj_data.polygon:
                abs_x = obj_data.x + pt[0]
                abs_y = obj_data.y + pt[1]

                self.points.append(
                    (abs_x, abs_y)
                )

        # Create collision rectangle
        if self.points:
            xs = [point[0] for point in self.points]
            ys = [point[1] for point in self.points]

            left = min(xs)
            right = max(xs)
            top = min(ys)
            bottom = max(ys)

            self.rect = pg.Rect(
                left,
                top,
                right - left,
                bottom - top
            )

        else:
            self.rect = pg.Rect(
                self.x,
                self.y,
                obj_data.width,
                obj_data.height
            )
