"""Simple A* pathfinding over TileMap tiles."""
from __future__ import annotations

from typing import List, Tuple, Optional
import heapq

from tilemap import TileMap


Coord = Tuple[int, int]


def _heuristic(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _neighbors(tm: TileMap, node: Coord) -> List[Coord]:
    x, y = node
    res: List[Coord] = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < tm.width and 0 <= ny < tm.height:
            res.append((nx, ny))
    return res


def _reconstruct(came_from: dict, current: Coord) -> List[Coord]:
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def find_path(tile_map: TileMap, start: Coord, goal: Coord) -> List[Coord]:
    """Find a path from start to goal using A*.

    Parameters
    ----------
    tile_map: TileMap
        Map defining the grid dimensions.
    start, goal: Tuple[int, int]
        Pixel coordinates for start and goal.

    Returns
    -------
    List of pixel coordinate steps (excluding the starting position).
    """

    # Convert pixel coordinates to tile coordinates
    start_tile = (start[0] // tile_map.tilewidth, start[1] // tile_map.tileheight)
    goal_tile = (goal[0] // tile_map.tilewidth, goal[1] // tile_map.tileheight)

    open_set: List[Tuple[int, Coord]] = []
    heapq.heappush(open_set, (0, start_tile))
    came_from: dict = {}
    g_score = {start_tile: 0}
    f_score = {start_tile: _heuristic(start_tile, goal_tile)}

    visited = set()
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal_tile:
            tiles = _reconstruct(came_from, current)
            if tiles and tiles[0] == start_tile:
                tiles = tiles[1:]
            return [
                (x * tile_map.tilewidth, y * tile_map.tileheight) for x, y in tiles
            ]
        if current in visited:
            continue
        visited.add(current)
        for neighbor in _neighbors(tile_map, current):
            tentative_g = g_score[current] + 1
            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + _heuristic(neighbor, goal_tile)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []
