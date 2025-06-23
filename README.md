This is a toy copy of the classic game Stick RPG.

Current features include a small city with several buildings. You can work, shop,
train at the gym, study at the library, and chat in the park. The player now has
strength, intelligence, and charisma stats that can be improved by visiting
these locations. The world runs on a 24-hour clock with automatic day changes.
Buildings keep regular hours and the city darkens at night.

Jobs now offer promotions based on your stats. The office rewards
intelligence and charisma while dealing drugs in the park relies on strength
and charisma. A new clinic job values intelligence and strength. Higher stats
increase your job level and the pay you receive. The park offers a riskier
"drug dealer" job at night that pays more but depends on strength and
charisma.

A new bar sells $10 tokens that can be used to play blackjack or the slots.
Win games to earn extra tokens, or lose them if luck is not on your side.

There is also a brawler waiting for challengers. Combat now uses your
strength, defense, and speed along with any bonuses from equipped gear. The
fighter with the higher speed strikes first and damage is reduced by defense.
Win a brawl and you pocket some cash.

The shop now stocks a few useful items: a cola to restore a little energy, a
protein bar for health, a book that teaches you intelligence, a gym pass that
builds strength, and a charm pendant that boosts charisma. You can also buy a
skateboard that lets you move 50% faster while holding the **Shift** key.
Basic equipment pieces like a leather helmet, leather armor, and boots can be
purchased and equipped through the inventory screen. A wooden sword is also
available for the weapon slot. Each item lists its attack (A), defense (D) and
speed (S) bonuses.



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


## Controls

- **Arrow keys/WASD**: Move
- **E**: Interact with nearby buildings
- **B/J/S/F**: Actions inside the bar

- **0-9**: Buy items in the shop
- **I**: Open inventory and equip gear
- **Shift**: Ride skateboard (if owned)

- **Q**: Leave a building
- **F5**: Save game
- **F9**: Load game

## Requirements

- Python 3.10+
- Pygame 2.0+

If the sound does not play, check that your system has an audio device and that Pygame's mixer can initialize.
