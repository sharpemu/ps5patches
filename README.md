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

1. Right-click the game in the library and select **Patches**.
2. Click **Download patches**. SharpEmu checks the title ID and installed game
   version, then downloads only matching XML files from this repository.
3. A dialog confirms completion, or explicitly reports that no compatible patch
   was found. Downloads are not enabled automatically.
4. Select a patch to read its author, notes and target version, then tick its
   checkbox to enable it.
5. Start the game. If it was already running, close it before changing patches.

You can also download XML files manually from `prospero_patches` and copy them
into `user/patches/` next to the SharpEmu executable. For example:

```text
SharpEmu/
  user/
    patches/
      DemonsSouls.xml
      Uncharted_LegacyThievesCollection.xml
```

Version-specific patches appear only when they match the installed game version.
`AppVer="mask"` entries are shown as **All versions (pattern matching)**. Selections
are saved per title ID and also apply when launching through the CLI. Both
folder-based games and `.zar` archives use the same patch settings.

Patches are disabled by default and modify loaded memory, not your game files or
archives. Updating a patch's contents requires enabling it again. Only enable
patches you trust.

## Developing Patches

Work from the executable for the exact title ID and game version you want to
support. You can inspect it in [Ghidra](https://ghidra-sre.org/) or
[IDA](https://hex-rays.com/ida-pro/) and edit the XML with a text editor such as
[Visual Studio Code](https://code.visualstudio.com/) or
[VSCodium](https://vscodium.com/).

Record the address base used for your patch in `ImageBase`; do not assume a fixed
base for every game. SharpEmu calculates each write as the loaded executable's
first loadable segment address plus `Address - ImageBase`. The resulting range
must be inside a loadable segment of the executable named by `AppElf`.

### Submission Guidelines

Add files as `prospero_patches/GameTitle.xml`. If a game already has a file, add
your patch to that file. Keep the original author credits and provide:

- `TitleID`: the supported `PPSA` title IDs.
- `Title`, `Name`, `Author` and `Note`: the game, patch name, creator and any
  instructions or warnings.
- `AppVer`: the exact game version, such as `01.004.000`, or `mask` when every
  line is pattern-based.
- `PatchVer`: the patch revision, separate from the game version.
- `AppElf`: the executable to patch, usually `eboot.bin`.
- `ImageBase`: the base address used when creating the patch addresses.

Use English game names for filenames, uppercase title IDs and lowercase hex for
addresses and byte values. Submit byte strings without spaces for consistency.
Keep separate `Metadata` entries for different target versions or executables.
Validate your patch on the exact game version before submitting.

The download index [`patches.json`](patches.json) is generated from XML `TitleID`
and `AppVer` fields, not game filenames. CI updates it automatically when patches
are added, changed or removed on `main`. To regenerate or check it locally:

```sh
python scripts/update_index.py
python scripts/update_index.py --check
```

### Patch Types

This reference covers the types listed by
[PS-Game-Patch](https://github.com/illusionyy/PS-Game-Patch/blob/main/.github/README.md).
**All eleven types below are supported by the current SharpEmu patch loader.**
Use a SharpEmu build containing typed and pattern-based patch support; the
initial patch manager supported only `bytes`.

| Type | Purpose | Value Example | SharpEmu Support |
| --- | --- | --- | --- |
| `byte` | 8-bit integer write | `0x12` | Yes |
| `bytes16` | 16-bit integer write | `0x1234` | Yes |
| `bytes32` | 32-bit integer write | `0x12345678` | Yes |
| `bytes64` | 64-bit integer write | `0x123456789abcdef0` | Yes |
| `bytes` | Raw hexadecimal byte sequence | `0102030405060708` | **Yes** |
| `float32` | Single-precision floating-point write | `1.0` | Yes |
| `float64` | Double-precision floating-point write | `1.0` | Yes |
| `utf8` | Null-terminated UTF-8 text write | `Hello World` | Yes |
| `utf16` | Null-terminated UTF-16LE text write | `Hello World` | Yes |
| `mask` | Pattern search with wildcard bytes and an `Offset` | `aa bb ?? dd` | Yes |
| `mask_jump32` | Pattern search followed by a 32-bit branch; uses `Target`, `Size` and `Offset` | `aa bb ?? dd` | Yes |

SharpEmu's current rules are:

- Integer values accept decimal notation or hexadecimal with `0x`, `#` or `$`.
  Negative values use two's complement. Out-of-range values are rejected instead
  of being truncated. Integers and floats are written in little-endian order.
- Floats use a decimal point regardless of the host language and must be finite
  and within range. `utf8` and `utf16` encode the literal XML text without a BOM
  and append a null terminator automatically. Unicode characters are supported;
  use `bytes` for custom encodings or termination.
- `bytes`, `mask` and `mask_jump32` replacement values contain a nonempty,
  even-length hexadecimal byte sequence without a prefix.
- `Address` and `ImageBase` are hexadecimal, optionally prefixed with `0x`.
  Omitting `ImageBase` treats `Address` as an offset from the first loadable
  segment of the executable.
- A patch may contain at most 4,096 lines and 1 MiB of replacement bytes in
  total, including generated branches and padding. Raw `bytes` lines are not
  restricted to the upstream 255-byte limit. XML files are limited to 4,194,304
  characters.
- Normally, `AppVer` must identify the installed game version. `AppVer="mask"`
  permits any version, but requires every line to use `mask` or `mask_jump32`.
- Fixed-address lines accept `Type`, `Address` and `Value`. Pattern lines also
  accept `Offset`; `mask_jump32` additionally requires `Target` and `Size`.
  Invalid types, values or extra line attributes reject the **whole patch**.

### Pattern Matching and Branches

For `mask`, `Address` is a whitespace-separated signature, not a number. Use
two-digit hexadecimal bytes and `?` or `??` for wildcard bytes. Signatures must
contain 1-255 bytes and at least one fixed byte. `Offset` is a signed decimal
offset from the first match; it defaults to zero.

Searches visit the target ELF's loadable segments in address order, never scan
unrelated mappings or gaps, and never match across segment boundaries. Lines
are resolved in XML order, so later searches see replacements staged by earlier
lines. Missing matches or invalid write ranges abort the whole patch before
anything is written.

For `mask_jump32`, `Target` is another signature locating the code cave, **not**
a numeric address. Both searches and both write ranges must be in executable
segments. `Size` is the number of bytes replaced at the source, from 5 to 256.
The loader writes an `E9 rel32` branch with NOP padding, puts the `Value` payload
at the code cave, then appends an `E9 rel32` branch back to source plus `Size`.
The source and code cave must not overlap, and both displacements must fit in
a signed 32-bit integer. Choose a unique code-cave signature, verify there is
space for the payload plus five return bytes, and ensure `Size` covers whole
instructions. The loader does not relocate overwritten instructions for you.

All writes are validated before they are committed. If a write fails, prior
writes, including the source branch and payload, are rolled back.

### Example Patch

The following adapts the upstream example to SharpEmu's typed writes. The
IDs and addresses are placeholders, **not a patch for a real game**. Replace
them with verified values before use. XML comments are allowed.

```xml
<?xml version="1.0" encoding="utf-8"?>
<Patch>
    <TitleID>
        <ID>PPSA00001</ID>
        <ID>PPSA00002</ID>
    </TitleID>
    <Metadata Title="Example Game"
              Name="Example Patch"
              Note="Describe the effect and any warnings here."
              Author="Your Name"
              PatchVer="1.0"
              AppVer="01.004.000"
              ImageBase="0x10000000"
              AppElf="eboot.bin">
        <PatchList>
            <!-- Supported: eight raw bytes at offset 0x10. -->
            <Line Type="bytes" Address="0x10000010" Value="0102030405060708"/>
            <Line Type="byte" Address="0x10000018" Value="255"/>
            <Line Type="bytes16" Address="0x1000001a" Value="0x1234"/>
            <Line Type="bytes32" Address="0x1000001c" Value="0x12345678"/>
            <Line Type="bytes64" Address="0x10000020" Value="0x0123456789abcdef"/>
            <Line Type="float32" Address="0x10000028" Value="1.5"/>
            <Line Type="float64" Address="0x10000030" Value="2.5"/>
            <!-- Text types append the correct null terminator automatically. -->
            <Line Type="utf8" Address="0x10000040" Value="Hello World"/>
            <Line Type="utf16" Address="0x10000060" Value="Hello World"/>
        </PatchList>
    </Metadata>
</Patch>
```

This separate pattern example also uses fictional signatures. The `mask`
replacement removes its own signature, while `mask_jump32` redirects a source
to a code cave and back:

```xml
<?xml version="1.0" encoding="utf-8"?>
<Patch>
    <TitleID><ID>PPSA00001</ID></TitleID>
    <Metadata Title="Example Game"
              Name="Pattern Example"
              Note="Fictional signatures; replace before use."
              Author="Your Name"
              PatchVer="1.0"
              AppVer="mask"
              AppElf="eboot.bin">
        <PatchList>
            <Line Type="mask" Address="48 8b ?? ?? 85 c0" Value="31c090909090"/>
            <Line Type="mask_jump32" Address="01 23 45 67 89"
                  Target="cc cc cc cc cc cc cc" Size="8" Value="31c0"/>
        </PatchList>
    </Metadata>
</Patch>
```

## Credits

The initial Demon's Souls and Uncharted XML patches are by
[illusion (illusionyy)](https://github.com/illusionyy), from
[PS-Game-Patch](https://github.com/illusionyy/PS-Game-Patch/tree/main/patches/xml_prospero).
Their original author metadata is preserved.

The patch type reference and XML example are adapted from the
[upstream documentation](https://github.com/illusionyy/PS-Game-Patch/blob/main/.github/README.md),
with SharpEmu's behavior and safety checks identified. Development and installation
instructions are specific to SharpEmu and this PS5-only collection.
