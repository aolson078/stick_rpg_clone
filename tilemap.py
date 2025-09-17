"""Simple TMX tilemap loader and renderer."""
import os
import xml.etree.ElementTree as ET
import pygame
from asset_utils import load_image

BUS_STOP_BUILDINGS = [
    {"rect": [260, 180, 40, 40], "name": "Downtown", "type": "bus_stop"},
    {"rect": [1820, 360, 40, 40], "name": "Mall", "type": "bus_stop"},
    {"rect": [2420, 920, 40, 40], "name": "Beach", "type": "bus_stop"},
]


class TileMap:
    """Load a TMX tilemap and render it using pygame."""

    def __init__(self, filename):
        self.filename = filename
        self.width = 0
        self.height = 0
        self.tilewidth = 0
        self.tileheight = 0
        self.layers = []
        self.tilesets = []  # list of (firstgid, [surface])
        self._load()

    def _load(self):
        tree = ET.parse(self.filename)
        root = tree.getroot()
        self.width = int(root.attrib["width"])
        self.height = int(root.attrib["height"])
        self.tilewidth = int(root.attrib["tilewidth"])
        self.tileheight = int(root.attrib["tileheight"])
        base_dir = os.path.dirname(self.filename)

        for ts in root.findall("tileset"):
            firstgid = int(ts.attrib["firstgid"])
            source = ts.attrib.get("source")
            if source:
                ts_root = ET.parse(os.path.join(base_dir, source)).getroot()
            else:
                ts_root = ts
            image = ts_root.find("image").attrib["source"]
            image_path = os.path.join(base_dir, image)
            tileset_image = load_image(image_path)
            columns = int(ts_root.attrib["columns"])
            tilecount = int(ts_root.attrib["tilecount"])
            tiles = []
            for i in range(tilecount):
                x = (i % columns) * self.tilewidth
                y = (i // columns) * self.tileheight
                surf = pygame.Surface((self.tilewidth, self.tileheight), pygame.SRCALPHA)
                surf.blit(
                    tileset_image, (0, 0), pygame.Rect(x, y, self.tilewidth, self.tileheight)
                )
                tiles.append(surf)
            self.tilesets.append((firstgid, tiles))
        self.tilesets.sort()

        for layer in root.findall("layer"):
            data = layer.find("data").text.strip().split(",")
            gids = [int(g) for g in data]
            self.layers.append(gids)

    def render(self, surface, cam_x=0, cam_y=0):
        """Blit the map's tiles to the surface offset by camera."""
        for layer in self.layers:
            for idx, gid in enumerate(layer):
                if gid == 0:
                    continue
                tileset = None
                firstgid = 0
                for fg, tiles in reversed(self.tilesets):
                    if gid >= fg:
                        tileset = tiles
                        firstgid = fg
                        break
                if tileset is None:
                    continue
                tile = tileset[gid - firstgid]
                x = (idx % self.width) * self.tilewidth - cam_x
                y = (idx // self.width) * self.tileheight - cam_y
                surface.blit(tile, (x, y))
