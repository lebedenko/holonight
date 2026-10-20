# Desktop session configuration overrides

Status: Proposed convention. No implementation completed as part of this proposal.

Applications may need different preferences in different desktop sessions without
duplicating their entire configuration. This convention defines how an application
selects one session override and combines it with its base configuration. It is
independent of HoloNight libraries, toolkits and file formats; each application owns
its schema, validation, persistence and configuration directory.

## Resolution and precedence

Resolve the application configuration directory beneath `$XDG_CONFIG_HOME`, falling
back to `$HOME/.config` when that variable is unset or empty. The examples below use
`<application>/config.toml`; TOML and that application directory are illustrative,
not shared schema requirements.

At application startup:

1. Start with built-in defaults.
2. Apply the application's base configuration, if present.
3. Split `XDG_CURRENT_DESKTOP` on colons, preserving order and ignoring empty entries.
   Normalize ASCII uppercase letters in each name to lowercase.
4. Look for the corresponding `config-<desktop>.toml` files in the same application
   directory. Select the first existing matching file and apply it as the sole
   session override.

For `XDG_CURRENT_DESKTOP=HoloNight-Hyprland:HoloNight:Hyprland`, lookup is exactly:

1. `config-holonight-hyprland.toml`
2. `config-holonight.toml`
3. `config-hyprland.toml`

Stop at the first existing match. Later candidates are not merged, even if they
contain settings omitted by the selected file. An absent session identity or no
matching override leaves the base configuration effective over built-in defaults.
There is no compositor detection or inference from running processes.

## Merge semantics

Apply settings individually within sections. An override replaces only the settings
it specifies; omitted settings inherit from the base configuration, or built-in
defaults when absent there too. A partial section does not replace the whole base
section. Arrays are replaced as whole values, never concatenated or merged by index.

Applications choose their filename extension and parsing rules while retaining this
selection order and merge model. They define supported desktop-name validation,
invalid-value and malformed-file handling, and diagnostics. Session names must be
treated as filename components within the application directory, not as paths.
An invalid selected file must not silently turn selection into merging later
candidates. Profile selection occurs at startup; any future reload behavior needs
an explicit application contract.

## Ownership and editing

This is a convention, not a shared configuration library or an extension to a shared
appearance schema. Adoption does not require a HoloNight dependency. Applications
retain responsibility for reading, validating and persisting their own preferences.

Configuration provenance distinguishes each effective setting's source: built-in
default, base file or selected session override. A future settings UI supporting
these layers must make the editing destination explicit. Editing the base may not
change a value shadowed by the selected override; editing the override affects only
that profile. Removing an override value restores inheritance. Saving a flattened
effective configuration into the base would lose these distinctions and must not be
an implicit editing operation. UI design and persistence mechanics remain outside
this proposal.

## Proposed adoption

The [Viewer session header preferences draft](../../holonight-viewer/docs/sdd/session-header-preferences/README.md)
applies this convention to application-local presentation preferences. Existing
runtime behavior and historical design records remain unchanged.
