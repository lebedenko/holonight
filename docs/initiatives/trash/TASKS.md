# Trash integration ledger

| Owner | Work package |
| --- | --- |
| Files | Ship the independent NFS Move to Trash fix and the provider-backed Trash view. |
| holonightd | Install and export the Trash library and the daily systemd user timer. |
| Settings | Edit and save the shared policy through the application footer. |
| Umbrella | Stage the provider and consumers in order, verify ownership, and perform native acceptance before rollout. |

Both consumer CI manifests pin the published holonightd revision. The umbrella
pins the published provider and consumers in dependency order.

| Repository | Published revision |
| --- | --- |
| holonightd | `af9c28553e3acb554111123bbd72fb90338040dc` |
| Files | `9bff50ac53e0968469ecc6d5b6f366364d2859e0` |
| Settings | `c75d5e3193d5809af9adef89f73411ead88c2600` |

Settings also includes the separately committed Appearance and Bluetooth lint
cleanup authorized during publication, `9f3e955`.

## Local acceptance

- Files passed its focused offscreen regressions, including alternate restore,
  permanent deletion confirmation and Empty Trash snapshot behavior.
- A private mount namespace backed by a disposable NFS directory verified fresh
  setgid Trash creation, collision handling, failed moves and retention in both
  per-volume layouts. A local fixture verified default ACL inheritance.
- Provider tests covered retention with an injected clock, invalid metadata,
  offline opt-ins, copy failures and concurrent restore and removal.
- Settings passed its offscreen Save/Discard round trip in both control styles.
- A transient user timer ran the staged one-shot with both apps closed.
- The staged install manifest assigns the user units and their relative
  `timers.target.wants` link to holonightd. The installer ownership suite passed.

- The user confirmed that the native checks passed, including the corrected
  Trash discovery warnings and HoloNight confirmation dialogs.

- Provider container acceptance passed. Files passed its full test suite,
  affected-code lint, QML checks and fresh installed-runtime acceptance.
- Settings passed all 110 tests, affected-code lint and installed startup under
  every supported style override. Existing Appearance and Bluetooth lint issues
  were corrected with their behavior covered by the existing tests.
