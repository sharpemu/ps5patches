# PS5 Game Patches

Community game patches for PlayStation 5 games, for use with
[SharpEmu](https://github.com/sharpemu/sharpemu).

Patch files are stored in [`prospero_patches`](prospero_patches). Each XML lists
the supported title IDs, game versions, target executables and patch authors.

## Available Patches

| Game | Game Versions | Patch File |
| --- | --- | --- |
| Demon's Souls | `01.000.000`, `01.004.000` | [DemonsSouls.xml](prospero_patches/DemonsSouls.xml) |
| Uncharted: Legacy of Thieves Collection | `01.000.000` | [Uncharted_LegacyThievesCollection.xml](prospero_patches/Uncharted_LegacyThievesCollection.xml) |

The Uncharted file contains separate entries for A Thief's End and The Lost
Legacy. A listed patch is not a guarantee of compatibility with every emulator
build; check its target version before using it.

## Using Patches in SharpEmu

1. Download the XML file for your game from `prospero_patches`.
2. Copy it into `user/patches/` next to the SharpEmu executable.
3. Right-click the game in the library and select **Patches**.
4. Select a patch to read its author, notes and target version, then tick its
   checkbox to enable it.
5. Start the game. If it was already running, close it before changing patches.

For example:

```text
SharpEmu/
  user/
    patches/
      DemonsSouls.xml
      Uncharted_LegacyThievesCollection.xml
```

Only patches matching the installed game version appear in the list. Selections
are saved per title ID and also apply when launching through the CLI. Both
folder-based games and `.zar` archives use the same patch settings.

Patches are disabled by default and modify loaded memory, not your game files or
archives. Updating a patch's contents requires enabling it again. Only enable
patches you trust.

## Contributing

Add files as `prospero_patches/GameTitle.xml`. If a game already has a file, add
your patch to that file. Keep the original author credits and provide:

- `TitleID`: the supported `PPSA` title IDs.
- `Title`, `Name`, `Author` and `Note`: the game, patch name, creator and any
  instructions or warnings.
- `AppVer`: the exact game version, such as `01.004.000`.
- `PatchVer`: the patch revision, separate from the game version.
- `AppElf`: the executable to patch, usually `eboot.bin`.
- `ImageBase`: the base address used when creating the patch addresses.

SharpEmu currently supports `Type="bytes"` writes. Use hexadecimal addresses and
even-length hexadecimal byte strings. Other line types and wildcard versions
are not supported by its patch loader.

The loader relocates each address from `ImageBase` to the loaded executable.
Validate the addresses against the exact game version before submitting.

## Credits

The initial Demon's Souls and Uncharted XML patches are by
[illusion (illusionyy)](https://github.com/illusionyy), from
[PS-Game-Patch](https://github.com/illusionyy/PS-Game-Patch/tree/main/patches/xml_prospero).
Their original author metadata is preserved.

This README's structure was informed by the
[upstream documentation](https://github.com/illusionyy/PS-Game-Patch/blob/main/.github/README.md),
with instructions specific to SharpEmu and this PS5-only collection.
