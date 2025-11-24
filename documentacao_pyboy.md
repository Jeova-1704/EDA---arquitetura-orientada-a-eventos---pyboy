Module pyboy
Expand source code
Sub-modules
pyboy.api
Tools to help interfacing with the Game Boy hardware

pyboy.plugins
Plugins that extend PyBoy's functionality. The only publicly exposed, are the game wrappers.

pyboy.utils
Classes
class PyBoy
(
gamerom, *, window='SDL2', scale=3, symbols=None, bootrom=None, sound_volume=100, sound_emulated=True, sound_sample_rate=None, cgb=None, gameshark=None, no_input=False, log_level='WARNING', color_palette=(16777215, 10066329, 5592405, 0), cgb_color_palette=((16777215, 8126257, 25541, 0), (16777215, 16745604, 9714234, 0), (16777215, 16745604, 9714234, 0)), title_status=False, **kwargs)
PyBoy is loadable as an object in Python. This means, it can be initialized from another script, and be controlled and probed by the script. It is supported to spawn multiple emulators, just instantiate the class multiple times.

A range of methods are exposed, which should allow for complete control of the emulator. Please open an issue on GitHub, if other methods are needed for your projects. Take a look at the files in examples/ for a crude "bots", which interact with the game.

Only the gamerom argument is required.

Example:

>>> pyboy = PyBoy('game_rom.gb')
>>> for _ in range(60): # Use 'while True:' for infinite
...     pyboy.tick()
True...
>>> pyboy.stop()

Args
gamerom : str
Filepath to a game-ROM for Game Boy or Game Boy Color.
Kwargs
window (str): "SDL2", "OpenGL", or "null"
scale (int): Window scale factor. Doesn't apply to API.
symbols (str): Filepath to a .sym file to use. If unsure, specify None.
bootrom (str): Filepath to a boot-ROM to use. If unsure, specify None.
sound_volume (int): Set sound volume in percent (0-100).
sound_emulated (bool): Disables sound emulation (not just muted!).
sound_sample_rate (int): Set sound sample rate. Has to be divisible in 60.
cgb (bool): Forcing Game Boy Color mode.
gameshark (str): GameShark codes to apply.
no_input (bool): Disable all user-input (mostly for autonomous testing)
log_level (str): "CRITICAL", "ERROR", "WARNING", "INFO" or "DEBUG"
color_palette (tuple): Specify the color palette to use for rendering.
cgb_color_palette (list of tuple): Specify the color palette to use for rendering in CGB-mode for non-color games.
title_status (bool): Enable performance status in window title
Plugin kwargs:
autopause (bool): Enable auto-pausing when window looses focus [plugin: AutoPause]
breakpoints (str): Add breakpoints on start-up (internal use) [plugin: DebugPrompt]
record_input (bool): Record user input and save to a file (internal use) [plugin: RecordReplay]
rewind (bool): Enable rewind function [plugin: Rewind]
Other keyword arguments may exist for plugins that are not listed here. They can be viewed by running pyboy --help in the terminal.

Expand source code
Instance variables
var screen
Use this method to get a Screen object. This can be used to get the screen buffer in a variety of formats.

It's also here you can find the screen position (SCX, SCY, WX, WY) for each scan line in the screen buffer. See Screen.tilemap_position_list for more information.

Example:

>>> pyboy.screen.image.show()
>>> pyboy.screen.ndarray.shape
(144, 160, 4)
>>> pyboy.screen.raw_buffer_format
'RGBA'

NOTE: See PyBoy.sound to get the sound buffer.

Returns
Screen: A Screen object with helper functions for reading the screen buffer.

var sound
Use this method to get a Sound object. This can be used to get the sound buffer of the latest screen frame (see PyBoy.screen).

Example:

>>> pyboy.sound.ndarray.shape # 801 samples, 2 channels (stereo)
(801, 2)
>>> pyboy.sound.ndarray
array([[0, 0],
       [0, 0],
       ...
       [0, 0],
       [0, 0]], dtype=int8)
Returns
Sound: A Sound object with helper functions for accessing the sound buffer.

var memory
Provides a PyBoyMemoryView object for reading and writing the memory space of the Game Boy.

For a more comprehensive description, see the PyBoyMemoryView class.

Example:

>>> pyboy.memory[0x0000:0x0010] # Read 16 bytes from ROM bank 0
[49, 254, 255, 33, 0, 128, 175, 34, 124, 254, 160, 32, 249, 6, 48, 33]
>>> pyboy.memory[1, 0x2000] = 12 # Override address 0x2000 from ROM bank 1 with the value 12
>>> pyboy.memory[0xC000] = 1 # Write to address 0xC000 with value 1
var register_file
Provides a PyBoyRegisterFile object for reading and writing the CPU registers of the Game Boy.

The register file is best used inside the callback of a hook, as PyBoy.tick() doesn't return at a specific point.

For a more comprehensive description, see the PyBoyRegisterFile class.

Example:

>>> def my_callback(register_file):
...     print("Register A:", register_file.A)
>>> pyboy.hook_register(0, 0x100, my_callback, pyboy.register_file)
>>> pyboy.tick(70)
Register A: 1
True
var memory_scanner
Provides a MemoryScanner object for locating addresses of interest in the memory space of the Game Boy. This might require some trial and error. Values can be represented in memory in surprising ways.

Open an issue on GitHub if you need finer control, and we will take a look at it.

Example:

>>> current_score = 4 # You write current score in game
>>> pyboy.memory_scanner.scan_memory(current_score, start_addr=0xC000, end_addr=0xDFFF)
[]
>>> for _ in range(175):
...     pyboy.tick(1, True) # Progress the game to change score
True...
>>> current_score = 8 # You write the new score in game
>>> from pyboy.api.memory_scanner import DynamicComparisonType
>>> addresses = pyboy.memory_scanner.rescan_memory(current_score, DynamicComparisonType.MATCH)
>>> print(addresses) # If repeated enough, only one address will remain
[]

var tilemap_background
The Game Boy uses two tile maps at the same time to draw graphics on the screen. This method will provide one for the background tiles. The game chooses whether it wants to use the low or the high tilemap.

Read more details about it, in the Pan Docs.

Example:

>>> pyboy.tilemap_background[8,8]
1
>>> pyboy.tilemap_background[7:12,8]
[0, 1, 0, 1, 0]
>>> pyboy.tilemap_background[7:12,8:11]
[[0, 1, 0, 1, 0], [0, 2, 3, 4, 5], [0, 0, 6, 0, 0]]

Returns
TileMap: A TileMap object for the tile map.

var tilemap_window
The Game Boy uses two tile maps at the same time to draw graphics on the screen. This method will provide one for the window tiles. The game chooses whether it wants to use the low or the high tilemap.

Read more details about it, in the Pan Docs.

Example:

>>> pyboy.tilemap_window[8,8]
1
>>> pyboy.tilemap_window[7:12,8]
[0, 1, 0, 1, 0]
>>> pyboy.tilemap_window[7:12,8:11]
[[0, 1, 0, 1, 0], [0, 2, 3, 4, 5], [0, 0, 6, 0, 0]]

Returns
TileMap: A TileMap object for the tile map.

var cartridge_title
The title stored on the currently loaded cartridge ROM. The title is all upper-case ASCII and may have been truncated to 11 characters.

Example:

>>> pyboy.cartridge_title # Title of PyBoy's default ROM
'DEFAULT-ROM'

Returns
str :
Game title
var game_wrapper
Provides an instance of a game-specific or generic wrapper. The game is detected by the cartridge's hard-coded game title (see PyBoy.cartridge_title).

If a game-specific wrapper is not found, a generic wrapper will be returned.

To get more information, find the wrapper for your game in pyboy.plugins.

Example:

>>> pyboy.game_wrapper.start_game()
>>> pyboy.game_wrapper.reset_game()

Returns
PyBoyGameWrapper: A game-specific wrapper object.

var gameshark
Provides an instance of the GameShark handler. This allows you to inject GameShark-based cheat codes.

Example:

>>> pyboy.gameshark.add("010138CD")
>>> pyboy.gameshark.remove("010138CD")
>>> pyboy.gameshark.clear_all()
Methods
def tick
(
self, count=1, render=True, sound=True)
Progresses the emulator ahead by count frame(s).

To run the emulator in real-time, it will need to process 60 frames a second (for example in a while-loop). This function will block for roughly 16,67ms per frame, to not run faster than real-time, unless you specify otherwise with the PyBoy.set_emulation_speed() method.

If you need finer control than 1 frame, have a look at PyBoy.hook_register() to inject code at a specific point in the game.

Setting render to True will make PyBoy render the screen for the last frame of this tick. This can be seen as a type of "frameskipping" optimization.

For AI training, it's adviced to use as high a count as practical, as it will otherwise reduce performance substantially. While setting render to False, you can still access the PyBoy.game_area() to get a simpler representation of the game.

If render was enabled, use Screen to get a NumPy buffer or raw memory buffer.

Example:

>>> pyboy.tick() # Progress 1 frame with rendering
True
>>> pyboy.tick(1) # Progress 1 frame with rendering
True
>>> pyboy.tick(60, False) # Progress 60 frames *without* rendering
True
>>> pyboy.tick(60, True) # Progress 60 frames and render *only the last frame*
True
>>> for _ in range(60): # Progress 60 frames and render every frame
...     if not pyboy.tick(1, True):
...         break
>>>
Args
count : int
Number of ticks to process
render : bool
Whether to render an image for this tick
Returns
(True or False): False if emulation has ended otherwise True

Expand source code
def stop
(
self, save=True)
Gently stops the emulator and all sub-modules.

Example:

>>> pyboy.stop() # Stop emulator and save game progress (cartridge RAM)
>>> pyboy.stop(False) # Stop emulator and discard game progress (cartridge RAM)

Args
save : bool
Specify whether to save the game upon stopping. It will always be saved in a file next to the provided game-ROM.
Expand source code
def button
(
self, input, delay=1)
Send input to PyBoy in the form of "a", "b", "start", "select", "left", "right", "up" and "down".

The button will automatically be released at the following call to PyBoy.tick().

Example:

>>> pyboy.button('a') # Press button 'a' and release after `pyboy.tick()`
>>> pyboy.tick() # Button 'a' pressed
True
>>> pyboy.tick() # Button 'a' released
True
>>> pyboy.button('a', 3) # Press button 'a' and release after 3 `pyboy.tick()`
>>> pyboy.tick() # Button 'a' pressed
True
>>> pyboy.tick() # Button 'a' still pressed
True
>>> pyboy.tick() # Button 'a' still pressed
True
>>> pyboy.tick() # Button 'a' released
True
Args
input : str
button to press
delay : int, optional
Number of frames to delay the release. Defaults to 1
Expand source code
def button_press
(
self, input)
Send input to PyBoy in the form of "a", "b", "start", "select", "left", "right", "up" and "down".

The button will remain press until explicitly released with PyBoy.button_release() or PyBoy.send_input().

Example:

>>> pyboy.button_press('a') # Press button 'a' and keep pressed after `PyBoy.tick()`
>>> pyboy.tick() # Button 'a' pressed
True
>>> pyboy.tick() # Button 'a' still pressed
True
>>> pyboy.button_release('a') # Release button 'a' on next call to `PyBoy.tick()`
>>> pyboy.tick() # Button 'a' released
True

Args
input : str
button to press
Expand source code
def button_release
(
self, input)
Send input to PyBoy in the form of "a", "b", "start", "select", "left", "right", "up" and "down".

This will release a button after a call to PyBoy.button_press() or PyBoy.send_input().

Example:

>>> pyboy.button_press('a') # Press button 'a' and keep pressed after `PyBoy.tick()`
>>> pyboy.tick() # Button 'a' pressed
True
>>> pyboy.tick() # Button 'a' still pressed
True
>>> pyboy.button_release('a') # Release button 'a' on next call to `PyBoy.tick()`
>>> pyboy.tick() # Button 'a' released
True

Args
input : str
button to release
Expand source code
def send_input
(
self, event, delay=0)
Send a single input to control the emulator. This is both Game Boy buttons and emulator controls. See WindowEvent for which events to send.

Consider using PyBoy.button() instead for easier access.

Example:

>>> from pyboy.utils import WindowEvent
>>> pyboy.send_input(WindowEvent.PRESS_BUTTON_A) # Press button 'a' and keep pressed after `PyBoy.tick()`
>>> pyboy.tick() # Button 'a' pressed
True
>>> pyboy.tick() # Button 'a' still pressed
True
>>> pyboy.send_input(WindowEvent.RELEASE_BUTTON_A) # Release button 'a' on next call to `PyBoy.tick()`
>>> pyboy.tick() # Button 'a' released
True
And even simpler with delay:

>>> from pyboy.utils import WindowEvent
>>> pyboy.send_input(WindowEvent.PRESS_BUTTON_A) # Press button 'a' and keep pressed after `PyBoy.tick()`
>>> pyboy.send_input(WindowEvent.RELEASE_BUTTON_A, 2) # Release button 'a' on third call to `PyBoy.tick()`
>>> pyboy.tick() # Button 'a' pressed
True
>>> pyboy.tick() # Button 'a' still pressed
True
>>> pyboy.tick() # Button 'a' released
True
Args
event : pyboy.WindowEvent
The event to send
delay : int
0 for immediately, number of frames to delay the input
Expand source code
def save_state
(
self, file_like_object)
Saves the complete state of the emulator. It can be called at any time, and enable you to revert any progress in a game.

You can either save it to a file, or in-memory. The following two examples will provide the file handle in each case. Remember to seek the in-memory buffer to the beginning before calling PyBoy.load_state():

>>> # Save to file
>>> with open("state_file.state", "wb") as f:
...     pyboy.save_state(f)
>>>
>>> # Save to memory
>>> import io
>>> with io.BytesIO() as f:
...     f.seek(0)
...     pyboy.save_state(f)
0

Args
file_like_object : io.BufferedIOBase
A file-like object for which to write the emulator state.
Expand source code
def load_state
(
self, file_like_object)
Restores the complete state of the emulator. It can be called at any time, and enable you to revert any progress in a game.

You can either load it from a file, or from memory. See PyBoy.save_state() for how to save the state, before you can load it here.

To load a file, remember to load it as bytes:

>>> # Load file
>>> with open("state_file.state", "rb") as f:
...     pyboy.load_state(f)
>>>
Args
file_like_object : io.BufferedIOBase
A file-like object for which to read the emulator state.
Expand source code
def game_area_dimensions
(
self, x, y, width, height, follow_scrolling=True)
If using the generic game wrapper (see PyBoy.game_wrapper), you can use this to set the section of the tilemaps to extract. This will default to the entire tilemap.

Example:

>>> pyboy.game_wrapper.shape
(32, 32)
>>> pyboy.game_area_dimensions(2, 2, 10, 18, False)
>>> pyboy.game_wrapper.shape
(10, 18)
Args
x : int
Offset from top-left corner of the screen
y : int
Offset from top-left corner of the screen
width : int
Width of game area
height : int
Height of game area
follow_scrolling : bool
Whether to follow the scrolling of SCX and SCY
Expand source code
def game_area_collision
(
self)
Some game wrappers define a collision map. Check if your game wrapper has this feature implemented: pyboy.plugins.

The output will be unique for each game wrapper.

Example:

>>> # This example show nothing, but a supported game will
>>> pyboy.game_area_collision()
array([[0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=uint32)

Returns
memoryview:
Simplified 2-dimensional memoryview of the collision map
Expand source code
def game_area_mapping
(
self, mapping, sprite_offset=0)
Define custom mappings for tile identifiers in the game area.

Example of custom mapping:

>>> from pyboy.api.constants import TILES
>>> mapping = [x for x in range(TILES)] # 1:1 mapping of 384 tiles
>>> mapping[0] = 0 # Map tile identifier 0 -> 0
>>> mapping[1] = 0 # Map tile identifier 1 -> 0
>>> mapping[2] = 0 # Map tile identifier 2 -> 0
>>> mapping[3] = 0 # Map tile identifier 3 -> 0
>>> pyboy.game_area_mapping(mapping, 1000)

Some game wrappers will supply mappings as well. See the specific documentation for your game wrapper: pyboy.plugins.

>>> pyboy.game_area_mapping(pyboy.game_wrapper.mapping_one_to_one, 0)

Args
mapping : list or ndarray
list of 384 (DMG) or 768 (CGB) tile mappings. Use None to reset to a 1:1 mapping.
sprite_offest : int
Optional offset add to tile id for sprites
Expand source code
def game_area
(
self)
Use this method to get a matrix of the "game area" of the screen. This view is simplified to be perfect for machine learning applications.

The layout will vary from game to game. Below is an example from Tetris:

Example:

>>> pyboy.game_area()
array([[ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
       [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
       [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
       [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
       [ 47,  47,  47, 130, 130,  47,  47,  47,  47,  47],
       [ 47,  47,  47,  47, 130, 130,  47,  47,  47,  47],
       [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
       [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
       [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
       [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
       [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
       [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
       [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
       [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
       [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
       [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
       [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
       [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47]], dtype=uint32)

If you want a "compressed", "minimal" or raw mapping of tiles, you can change the mapping using PyBoy.game_area_mapping(). Either you'll have to supply your own mapping, or you can find one that is built-in with the game wrapper plugin for your game. See PyBoy.game_area_mapping().

Returns
memoryview:
Simplified 2-dimensional memoryview of the screen
Expand source code
def set_emulation_speed
(
self, target_speed)
Set the target emulation speed. It might loose accuracy of keeping the exact speed, when using a high target_speed.

The speed is defined as a multiple of real-time. I.e target_speed=2 is double speed.

A target_speed of 0 means unlimited. I.e. fastest possible execution.

Due to backwards compatibility, the null window starts at unlimited speed (i.e. target_speed=0), while others start at realtime (i.e. target_speed=1).

Example:

>>> pyboy.tick() # Delays 16.67ms
True
>>> pyboy.set_emulation_speed(0) # Disable limit
>>> pyboy.tick() # As fast as possible
True
Args
target_speed : int
Target emulation speed as multiplier of real-time.
Expand source code
def symbol_lookup
(
self, symbol)
Look up a specific symbol from provided symbols file.

This can be useful in combination with PyBoy.memory or even PyBoy.hook_register().

See PyBoy.hook_register() for how to load symbol into PyBoy.

Example:

>>> # Directly
>>> pyboy.memory[pyboy.symbol_lookup("Tileset")]
0
>>> # By bank and address
>>> bank, addr = pyboy.symbol_lookup("Tileset")
>>> pyboy.memory[bank, addr]
0
>>> pyboy.memory[bank, addr:addr+10]
[0, 0, 0, 0, 0, 0, 102, 102, 102, 102]

Returns
(int, int): ROM/RAM bank, address

Expand source code
def hook_register
(
self, bank, addr, callback, context)
Adds a hook into a specific bank and memory address. When the Game Boy executes this address, the provided callback function will be called.

By providing an object as context, you can later get access to information inside and outside of the callback.

Example:

>>> context = "Hello from hook"
>>> def my_callback(context):
...     print(context)
>>> pyboy.hook_register(0, 0x100, my_callback, context)
>>> pyboy.tick(70)
Hello from hook
True

If a symbol file is loaded, this function can also automatically resolve a bank and address from a symbol. To enable this, you'll need to place a .sym file next to your ROM, or provide it using: PyBoy(..., symbols="game_rom.gb.sym").

Then provide None for bank and the symbol for addr to trigger the automatic lookup.

Example:

>>> # Continued example above
>>> pyboy.hook_register(None, "Main.move", lambda x: print(x), "Hello from hook2")
>>> pyboy.tick(81)
Hello from hook2
True

NOTE:

Don't register hooks to something that isn't executable (graphics data etc.). This will cause your game to show weird behavior or crash. Hooks are installed by replacing the instruction at the bank and address with a special opcode (0xDB). If the address is read by the game instead of executed as code, this value will be read instead.

Args
bank : int or None
ROM or RAM bank (None for symbol lookup)
addr : int or str
Address in the Game Boy's address space (str for symbol lookup)
callback : func
A function which takes context as argument
context : object
Argument to pass to callback when hook is called
Expand source code
def hook_deregister
(
self, bank, addr)
Remove a previously registered hook from a specific bank and memory address.

Example:

>>> context = "Hello from hook"
>>> def my_callback(context):
...     print(context)
>>> pyboy.hook_register(0, 0x2000, my_callback, context)
>>> pyboy.hook_deregister(0, 0x2000)

This function can also deregister a hook based on a symbol. See PyBoy.hook_register() for details.

Example:

>>> pyboy.hook_register(None, "Main", lambda x: print(x), "Hello from hook")
>>> pyboy.hook_deregister(None, "Main")

Args
bank : int or None
ROM or RAM bank (None for symbol lookup)
addr : int or str
Address in the Game Boy's address space (str for symbol lookup)
Expand source code
def get_sprite
(
self, sprite_index)
Provides a Sprite object, which makes the OAM data more presentable. The given index corresponds to index of the sprite in the "Object Attribute Memory" (OAM).

The Game Boy supports 40 sprites in total. Read more details about it, in the Pan Docs.

>>> s = pyboy.get_sprite(12)
>>> s
Sprite [12]: Position: (-8, -16), Shape: (8, 8), Tiles: (Tile: 0), On screen: False
>>> s.on_screen
False
>>> s.tiles
[Tile: 0]

Args
index : int
Sprite index from 0 to 39.
Returns
Sprite: Sprite corresponding to the given index.

Expand source code
def get_sprite_by_tile_identifier
(
self, tile_identifiers, on_screen=True)
Provided a list of tile identifiers, this function will find all occurrences of sprites using the tile identifiers and return the sprite indexes where each identifier is found. Use the sprite indexes in the PyBoy.get_sprite() function to get a Sprite object.

Example:

>>> print(pyboy.get_sprite_by_tile_identifier([43, 123]))
[[0, 2, 4], []]

Meaning, that tile identifier 43 is found at the sprite indexes: 0, 2, and 4, while tile identifier 123 was not found anywhere.

Args
identifiers : list
List of tile identifiers (int)
on_screen : bool
Require that the matched sprite is on screen
Returns
list:
list of sprite matches for every tile identifier in the input
Expand source code
def get_tile
(
self, identifier)
The Game Boy can have 384 tiles loaded in memory at once (768 for Game Boy Color). Use this method to get a Tile-object for given identifier.

The identifier is a PyBoy construct, which unifies two different scopes of indexes in the Game Boy hardware. See the Tile object for more information.

Example:

>>> t = pyboy.get_tile(2)
>>> t
Tile: 2
>>> t.shape
(8, 8)

Returns
Tile: A Tile object for the given identifier.

Expand source code
def rtc_lock_experimental
(
self, enable)
WARN: This is an experimental API and is subject to change.

Lock the Real Time Clock (RTC) of a supporting cartridge. It might be advantageous to lock the RTC when training an AI in games that use it to change behavior (i.e. day and night).

The first time the game is turned on, an .rtc file is created with the current time. This is the epoch for the RTC. When using rtc_lock_experimental, the RTC will always report this point in time. If you let the game progress first, before using rtc_lock_experimental, the internal clock will move backwards and might corrupt the game.

Example:

>>> pyboy = PyBoy('game_rom.gb')
>>> pyboy.rtc_lock_experimental(True) # RTC will not progress
WARN: This is an experimental API and is subject to change.

Args
enable : bool
True to lock RTC, False to operate normally
Expand source code
class PyBoyMemoryView
(
mb)
This class cannot be used directly, but is accessed through PyBoy.memory.

This class serves four purposes: Reading memory (ROM/RAM), writing memory (RAM), overriding memory (ROM) and special registers.

See the Pan Docs: Memory Map for a great overview of the memory space.

Memory can be accessed as individual bytes (pyboy.memory[0x00]) or as slices (pyboy.memory[0x00:0x10]). And if applicable, a specific ROM/RAM bank can be defined before the address (pyboy.memory[0, 0x00] or pyboy.memory[0, 0x00:0x10]).

The boot ROM is accessed using the special -1 ROM bank.

The find addresses of interest, either search online for something like: "[game title] RAM map", or find them yourself using PyBoy.memory_scanner.

Read:

If you're developing a bot or AI with this API, you're most likely going to be using read the most. This is how you would efficiently read the score, time, coins, positions etc. in a game's memory.

At this point, all reads will return a new list of the values in the given range. The slices will not reference back to the PyBoy memory. This feature might come in the future.

>>> pyboy.memory[0x0000] # Read one byte at address 0x0000
49
>>> pyboy.memory[0x0000:0x0010] # Read 16 bytes from 0x0000 to 0x0010 (excluding 0x0010)
[49, 254, 255, 33, 0, 128, 175, 34, 124, 254, 160, 32, 249, 6, 48, 33]
>>> pyboy.memory[-1, 0x0000:0x0010] # Read 16 bytes from 0x0000 to 0x0010 (excluding 0x0010) from the boot ROM
[49, 254, 255, 33, 0, 128, 175, 34, 124, 254, 160, 32, 249, 6, 48, 33]
>>> pyboy.memory[0, 0x0000:0x0010] # Read 16 bytes from 0x0000 to 0x0010 (excluding 0x0010) from ROM bank 0
[64, 65, 66, 67, 68, 69, 70, 65, 65, 65, 71, 65, 65, 65, 72, 73]
>>> pyboy.memory[2, 0xA000] # Read from external RAM on cartridge (if any) from bank 2 at address 0xA000
0
Write:

Writing to Game Boy memory can be complicated because of the limited address space. There's a lot of memory that isn't directly accessible, and can be hidden through "memory banking". This means that the same address range (for example 0x4000 to 0x8000) can change depending on what state the game is in.

If you want to change an address in the ROM, then look at override below. Issuing writes to the ROM area actually sends commands to the Memory Bank Controller (MBC) on the cartridge.

A write is done by assigning to the PyBoy.memory object. It's recommended to define the bank to avoid mistakes (pyboy.memory[2, 0xA000]=1). Without defining the bank, PyBoy will pick the current bank for the given address if needed (pyboy.memory[0xA000]=1).

>>> pyboy.memory[0xC000] = 123 # Write to WRAM at address 0xC000
>>> pyboy.memory[0xC000:0xC00A] = [0,1,2,3,4,5,6,7,8,9] # Write to WRAM from address 0xC000 to 0xC00A
>>> pyboy.memory[0xC010:0xC01A] = 0 # Write to WRAM from address 0xC010 to 0xC01A
>>> pyboy.memory[0x1000] = 123 # Not writing 123 at address 0x1000! This sends a command to the cartridge's MBC.
>>> pyboy.memory[2, 0xA000] = 123 # Write to external RAM on cartridge (if any) for bank 2 at address 0xA000
>>> # Game Boy Color (CGB) only:
>>> pyboy_cgb.memory[1, 0x8000] = 25 # Write to VRAM bank 1 at address 0xD000 when in CGB mode
>>> pyboy_cgb.memory[6, 0xD000] = 25 # Write to WRAM bank 6 at address 0xD000 when in CGB mode
Override:

Override data at a given memory address of the Game Boy's ROM.

This can be used to reprogram a game ROM to change its behavior.

This will not let you override RAM or a special register. This will let you override data in the ROM at any given bank. This is the memory allocated at 0x0000 to 0x8000, where 0x4000 to 0x8000 can be changed from the MBC.

NOTE: Any changes here are not saved or loaded to game states! Use this function with caution and reapply any overrides when reloading the ROM.

To override, it's required to provide the ROM-bank you're changing. Otherwise, it'll be considered a regular 'write' as described above.

>>> pyboy.memory[0, 0x0010] = 10 # Override ROM-bank 0 at address 0x0010
>>> pyboy.memory[0, 0x0010:0x001A] = [0,1,2,3,4,5,6,7,8,9] # Override ROM-bank 0 at address 0x0010 to 0x001A
>>> pyboy.memory[-1, 0x0010] = 10 # Override boot ROM at address 0x0010
>>> pyboy.memory[1, 0x6000] = 12 # Override ROM-bank 1 at address 0x6000
>>> pyboy.memory[0x1000] = 12 # This will not override, as there is no ROM bank assigned!
Special Registers:

The Game Boy has a range of memory addresses known as hardware registers. These control parts of the hardware like LCD, Timer, DMA, serial and so on. Even though they might appear as regular RAM addresses, reading/writing these addresses often results in special side-effects.

The DIV (0xFF04) register for example provides a number that increments 16 thousand times each second. This can be used as a source of randomness in games. If you read the value, you'll get a pseudo-random number. But if you write any value to the register, it'll reset to zero.

>>> pyboy.memory[0xFF04] # DIV register
231
>>> pyboy.memory[0xFF04] = 123 # Trying to write to it will always reset it to zero
>>> pyboy.memory[0xFF04]
0
Expand source code
class PyBoyRegisterFile
(
cpu)
This class cannot be used directly, but is accessed through PyBoy.register_file.

This class serves the purpose of reading and writing to the CPU registers. It's best used inside the callback of a hook, as PyBoy.tick() doesn't return at a specific point.

See the Pan Docs: CPU registers and flags for a great overview.

Registers are accessed with the following names: A, F, B, C, D, E, HL, SP, PC where the last three are 16-bit and the others are 8-bit. Trying to write a number larger than 8 or 16 bits will truncate it.

Example:

>>> def my_callback(pyboy):
...     print("Register A:", pyboy.register_file.A)
...     pyboy.memory[0xFF50] = 1 # Example: Disable boot ROM
...     pyboy.register_file.A = 0x11 # Modify to the needed value
...     pyboy.register_file.PC = 0x100 # Jump past existing code
>>> pyboy.hook_register(-1, 0xFC, my_callback, pyboy)
>>> pyboy.tick(120)
Register A: 1
True
Expand source code
Instance variables
var A
Expand source code
var F
Expand source code
var B
Expand source code
var C
Expand source code
var D
Expand source code
var E
Expand source code
var HL
Expand source code
var SP
Expand source code
var PC
Expand source code
Index
Sub-modules
pyboy.api
pyboy.plugins
pyboy.utils
Classes
PyBoy
tick
stop
button
button_press
button_release
send_input
save_state
load_state
game_area_dimensions
game_area_collision
game_area_mapping
game_area
set_emulation_speed
symbol_lookup
hook_register
hook_deregister
get_sprite
get_sprite_by_tile_identifier
get_tile
rtc_lock_experimental
screen
sound
memory
register_file
memory_scanner
tilemap_background
tilemap_window
cartridge_title
game_wrapper
gameshark
PyBoyMemoryView
PyBoyRegisterFile
A
F
B
C
D
E
HL
SP
PC
Generated by pdoc 0.11.5.