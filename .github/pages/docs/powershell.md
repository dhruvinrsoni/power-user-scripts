# PowerShell profiles

A PowerShell setup that loads `posh-git`, sets a colored prompt, applies
console fonts, and dot-sources persistent function libraries (the
`doskeys` aliases) so they survive across sessions.

## Active profiles

| File | What it does |
|---|---|
| [`Microsoft.PowerShell_profile.ps1`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/powershell/Microsoft.PowerShell_profile.ps1) | Configures buffer size, imports the console-font module, loads `posh-git`, and dot-sources the doskeys function libraries into the global scope. |
| [`profile.ps1`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/powershell/profile.ps1) | Imports `posh-git`, applies custom prompt colors (blue/teal backgrounds with fg symbols). Skips initialization in the Cursor Agent terminal so it doesn't fight the IDE. |

## Bundled modules

- **PSReadLine 2.3.5** — vendored under
  [`powershell/Modules/PSReadLine/2.3.5`](https://github.com/dhruvinrsoni/power-user-scripts/tree/main/powershell/Modules/PSReadLine).
  Includes a `SamplePSReadLineProfile.ps1` for tweaking history,
  completion, and key bindings.
- **SetConsoleFont** — module under
  [`powershell/Modules/SetConsoleFont`](https://github.com/dhruvinrsoni/power-user-scripts/tree/main/powershell/Modules/SetConsoleFont)
  for switching the console font from script.

## Bundled fonts

- `JetBrainsMonoRegularWindows.ttf`
- `JetBrains Mono Regular Nerd Font Complete Windows Compatible.ttf`

Drop into `C:\Windows\Fonts` (or right-click → Install).

## Installation

Locate your PowerShell profile path with `$PROFILE`, then point it at
this repo's profile:

```powershell
. "$HOME\path\to\power-user-scripts\powershell\profile.ps1"
```

Or replace the contents of `$PROFILE` with the file you want.
