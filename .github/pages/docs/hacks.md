# Hacks & tweaks

Experimental Windows tweaks: registry edits, Group Policy notes, an
Excel VBA logger, and a bookmark to ANSICON. Apply at your own risk —
many of these poke at system-level settings.

!!! warning "Heads up"
    Registry tweaks (`.reg` files) modify Windows system state. Read
    them before double-clicking, and back up the relevant keys first
    (`File → Export` in `regedit`).

## Excel VBA

| File | Purpose |
|---|---|
| [`Excel-VBA-script-to-log-every-change-in-a-sheet.js`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/Hacks/Excel-VBA-script-to-log-every-change-in-a-sheet.js) | Logs every cell change in a sheet (default name `Use Cases`) to a password-protected `Change Log` sheet. |

## Bookmarks

| File | Purpose |
|---|---|
| [`ansicon.url`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/Hacks/ansicon.url) | Shortcut to the ANSICON GitHub repo (ANSI color support for Windows terminal). |

## Registry tweaks

CMD-experience tweaks:

| File | Purpose |
|---|---|
| `AutoRun.reg` | Sets CMD completion chars, delayed expansion, auto-runs `doskeys.cmd`. |
| `CommandProcessorAll.reg` | Configures CMD completion, default color, extensions, delayed expansion, auto-runs `doskeys.cmd`. |
| `DelayedExpansion.reg` | Enables delayed expansion in CMD. |

System / UI tweaks:

| File | Purpose |
|---|---|
| `ActivateWindowOnHover.regedit.txt` | Pointer to "activate window by hover" Control Panel setting. |
| `LastActiveClick.reg` | Explorer setting: record last active click for UI state. |
| `RemoveAutoPinningInTaskbar.regedit.txt` | Reference to taskbar shell folder layout XML. |
| `ShowSecondsInSystemClock.regedit.txt` | Reference for showing seconds in the system clock. |
| `TaskbarCopilot.regedit.txt` | Reference for the Copilot taskbar button setting. |
| `TurnOffWindowsCopilot-Disabled.reg` | Sets `TurnOffWindowsCopilot=0` (Copilot enabled). |

Power & sleep:

| File | Purpose |
|---|---|
| `ScreenSaveTimeOut.reg` | Sets screen-saver timeout to 300 seconds (5 min). |
| `SystemUnattendedSleepTimeoutAttribute1to2.reg` | Reveals the unattended sleep-timeout option in Power settings. |
| `hibernate.regedit.txt` | Reference for hibernation power-setting registry path. |

Other:

| File | Purpose |
|---|---|
| `WSLExtendedKey_ForOptionWithoutShift.reg` | Adds WSL context-menu entry; access without holding Shift. |
| `update.reg` | Windows Update policy: version 2004, auto-update disabled, quality updates paused. |

Folder: [`Hacks/registry/`](https://github.com/dhruvinrsoni/power-user-scripts/tree/main/Hacks/registry)

## Group Policy notes

Reference snippets describing settings under `gpedit.msc`. Documentation
only — no automation.

| File | Topic |
|---|---|
| `Sleep Settings - Require-a-password-when-computer-wakes-up.txt` | Sleep / wake password policy |
| `Widgets Allow Widgets Set to Disable.txt` | Disabling Widgets |
| `Screen-saver-timeout.txt` | Screen-saver timeout under Personalization |

Folder: [`Hacks/Group Policy Editor (gpedit.msc)/`](https://github.com/dhruvinrsoni/power-user-scripts/tree/main/Hacks/Group%20Policy%20Editor%20(gpedit.msc))
