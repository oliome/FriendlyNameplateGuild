# FriendlyNameplateGuild

A lightweight **World of Warcraft: Forever** addon that displays guild names beneath friendly players' nameplates.

## Features

- Adds a separate `<Guild Name>` line beneath a player's name.
- Choose the guild text's color, font size, and spacing.
- Preview your changes in the settings window.
- Toggle guild labels on or off and reset settings to defaults.
- Saves your preferences between sessions.

## Installation

1. [Download the addon](downloads/FriendlyNameplateGuild.zip?raw=true).
2. Extract the `FriendlyNameplateGuild` folder into `_forever_/Interface/AddOns`.
3. Restart WoW and enable **FriendlyNameplateGuild** in the AddOns menu.
4. Enable **friendly player nameplates** in the game's settings. Use name-only mode if you prefer names without health bars.

If upgrading from the addon's previous name, remove its old folder to avoid duplicate labels.

## Settings

Type **`/fng`** or **`/friendlynameplateguild`** to open the settings window. Changes apply immediately.

Use `/fng status` to check whether guild labels are active.

## Current limitations

This is a **preview release**. Guild labels currently appear only in the open world, outside combat. Players without a guild, hostile players, and NPCs receive no label. Other nameplate addons may not be compatible.

The addon requires friendly player nameplates and leaves existing player names and their colors unchanged.
