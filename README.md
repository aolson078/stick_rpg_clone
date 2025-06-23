This is a toy copy of the classic game Stick RPG.

Current features include a small city with several buildings. You can work, shop,
train at the gym, study at the library, and chat in the park. The player now has
strength, intelligence, and charisma stats that can be improved by visiting
these locations. The world runs on a 24-hour clock with automatic day changes.
Buildings keep regular hours and the city darkens at night.


these locations. The world runs on a 24-hour clock with automatic day changes.
Buildings keep regular hours and the city darkens at night.

The game now features simple sound effects, looping background music, and a
stick-figure sprite with a two-frame walking animation.

There are a few simple quests to guide you, such as earning a set amount of
cash or raising your stats. The current quest is shown under the stats bar.

Random encounters can also happen while walking around. These short events may
reward or penalize you with money, stats, or health, adding some surprise to
each day.

You can save your progress with **F5** and load it back with **F9**. If a
`savegame.json` file exists, it will automatically be loaded when the game
starts.

## Getting Started

1. **Obtain the code**
   Clone your own copy of this repository or simply use the source files from
   this conversation. If you cloned it, `cd` into the new folder.
2. **Install Python 3 and Pygame**
   Make sure you have Python 3.10 or newer installed. Then install Pygame:
   ```bash
   pip install pygame
   ```
3. **Run the game**
   ```bash
   python game.py
   ```
   The window will open in 800x600 resolution. Use the arrow keys or WASD to move around.

### Asset setup

Binary assets (images and sound files) are not included in this repository. Create an
`assets` folder alongside the Python files and place the following files in it:

```
assets/enter.wav
assets/music.wav
assets/quest.wav
assets/step.wav
assets/player_0.png
assets/player_1.png
assets/player_2.png
```

You can supply your own audio and sprite files or copy them from another source.

## Controls

- **Arrow keys/WASD**: Move
- **E**: Interact with nearby buildings
- **Q**: Leave a building
- **F5**: Save game
- **F9**: Load game

## Requirements

- Python 3.10+
- Pygame 2.0+

If the sound does not play, check that your system has an audio device and that Pygame's mixer can initialize.
