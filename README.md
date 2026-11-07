# FriendlyNameplateGuild

A lightweight **World of Warcraft: Forever** addon that displays guild names beneath friendly players' nameplates.

## Features

- Adds a separate `<Guild Name>` line beneath a player's name.
- Choose the guild text's color, font size, and spacing.
- Preview your changes in the settings window.
- Enable WoW's name-only mode directly from the settings window to hide friendly health bars.
- Toggle guild labels on or off and reset settings to defaults.
- Saves your preferences between sessions.

## Installation

1. [Download the addon](downloads/FriendlyNameplateGuild.zip?raw=true).
2. Extract the `FriendlyNameplateGuild` folder into `_forever_/Interface/AddOns`.
3. Restart WoW and enable **FriendlyNameplateGuild** in the AddOns menu.
4. Enable **friendly player nameplates** in the game's settings. Open `/fng` and enable **Show names only** for the recommended layout without friendly health bars.

If upgrading from the addon's previous name, remove its old folder to avoid duplicate labels.

## Settings

Type **`/fng`** or **`/friendlynameplateguild`** to open the settings window. Changes apply immediately.

**Show names only** controls WoW's own friendly-player nameplate setting. The addon reads your existing choice and changes it only when you click the checkbox, outside combat. Turning guild labels off or resetting their appearance does not reset this game setting.

Use `/fng status` to check whether guild labels are active.

## Current limitations

This is a **preview release**. Guild labels currently appear only in the open world, outside combat. Players without a guild, hostile players, and NPCs receive no label. Other nameplate addons may not be compatible.

The addon requires friendly player nameplates and leaves existing player names and their colors unchanged.
