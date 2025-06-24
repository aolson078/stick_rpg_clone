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

The Bar is now a separate interior screen. Walk around inside to find the
counter for buying tokens, a blackjack table, slot machines, and a ring for
brawling. Move to the door and press **E** to leave.

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
Prices have been raised across the board and jobs pay a bit less, so it takes
time to afford the best gear and home upgrades.

Your apartment can also be improved. While inside the Home you can buy a Comfy
Bed, Decorations, or a Study Desk. These upgrades cost quite a bit but boost
your energy recovery and may grant daily bonuses when you sleep. The Home is
now a separate screen
you can walk around in—approach the bed and press **E** to sleep, or step to the
door and hit **E** to leave.

As your stats reach new milestones you earn perk points. Press **P** to open the
Perk menu and spend these points to unlock or upgrade perks (up to level 3).
Available perks include Gym Rat, Book Worm, Social Butterfly, Night Owl, Lucky,
and Iron Will. Higher perk levels further improve their bonuses.

Winning fights in the bar now progresses through five increasingly tough
challengers. Defeat them all to earn the hidden **Bar Champion** perk. Owning
every home upgrade unlocks **Home Owner**, and maxing out all other perks grants
the secret **Perk Master** perk.

A shady **Alley** building lets you battle random enemies for cash and the
occasional token. Victories count toward quest progress and scale in difficulty
over time.

The city also has a **Pet Shop** where you can adopt an animal companion.
Pets grant small bonuses like extra defense or charisma and may help you find
money or tokens.



The game now features simple sound effects, looping background music, and a
stick-figure sprite with a two-frame walking animation.

A short quest line walks you through the basics: earning money, training, and
taking on thugs in the new Alley location. Press **L** at any time to open the
quest log and review your progress. The current quest also appears under the
stats bar.

Random encounters can also happen while walking around. These short events may
reward or penalize you with money, stats, or health, adding some surprise to
each day. Certain encounters only appear at specific times such as early
morning joggers or late-night food stands.

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
   The window will open in 1600x1200 resolution. Use the arrow keys or WASD to move around.


## Controls

- **Arrow keys/WASD**: Move
- **E**: Interact with nearby buildings
- **E** near bar objects: Buy tokens, gamble, or fight

- **0-9**: Buy items in the shop
- **1-3**: Adopt a pet in the Pet Shop
- **I**: Open inventory and equip gear
- **Shift**: Ride skateboard (if owned)
- **T**: Skip 3 in-game hours
- **L**: View quest log

- **Q**: Leave a building
- **F5**: Save game
- **F9**: Load game

## Requirements

- Python 3.10+
- Pygame 2.0+

If the sound does not play, check that your system has an audio device and that Pygame's mixer can initialize.
