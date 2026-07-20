---
inclusion: manual
description: GPL Debugger documentation — how to enable, enter, and use the in-game GPL debugger
---

# GPL Debugger

The game contains an integrated, source-level debugger for the GPL scripting language.

## Enabling the Debugger

The debugger must be enabled at game startup. Two methods:

1. **Command line switch**: Use `-gpldebug` when starting the game.
2. **MajXPrefs file**: Edit the `MajXPrefs` file in `My Documents/My Games/MajestyHD`. Change the `UseGPLDebugger` tag to a value of `1`.

## SDK Code vs Standard Data

When the GPL debugger is active, the game switches to using the compiled GPL code in the SDK folder rather than the standard data folders. The compiled code in both locations has the same functionality, but the SDK version's debugging symbols match the source supplied by the SDK. The SDK source files differ from the originals only in formatting and commenting.

## Entering the Debugger

In-game hotkeys for debugger access:

| Key | Function |
|-----|----------|
| `_` (underscore) | Opens the debugger immediately |
| `\|` (vertical bar) | Sets a breakpoint on the **specific selected object** — triggers when that object runs any GPL code |
| `+` (plus) | Sets a breakpoint on the **type** of the selected object — triggers when any object of that type runs GPL code |

**Note:** When using the breakpoint keys (`|` and `+`), first select a unit on the map (hero, henchman, building, or any selectable item). The game may not immediately break into the debugger because objects do not run GPL every frame.

## Panels

The debugger has five panels, selected by buttons at the bottom of each panel:

### 1. Debugger (Line Debugger Panel)

Displays the currently running GPL source line, the call stack, and calling agent information. This panel appears on top when a breakpoint is hit.

**Top controls:**
- **Function dropdown** — shows the name of the current GPL function in the source window
- **Step buttons** (to the right of the dropdown):

| Button | Behavior |
|--------|----------|
| **Step Into** | If the current line contains a GPL function, steps into it. If not (or it's a C++ function), executes the line and moves to the next. |
| **Step Over** | Executes ALL GPL operations on the current line and moves to the next line. Stepping over the last line in a function exits the debugger and continues the game. |
| **Step Out** | Executes all remaining operations in the current function, re-enters the debugger at the next line in the calling function. At the top-level function, exits the debugger and resumes the game. |
| **Micro Step** | Executes a SINGLE GPL operation on the current line and returns to the debugger. Unlike Step Over, which runs all operations on a line. |
| **Show Next** | Restores the source view to the line containing the current execution point. |

**Secondary display window** (below the source window) — controlled by three buttons:

| Button | Shows |
|--------|-------|
| **Locals** | Values of all local variables in the currently executing GPL function |
| **Calling Agent** | The calling agent's member values |
| **Call Stack** | Current GPL call stack, agent name that called the function, and function trigger time |

**Toggle Breakpoint** button — toggles a breakpoint on the currently selected line in the source window.

### 2. Breakpoints (Break Points Panel)

Displays active breakpoints. Allows clearing them or changing their properties.

### 3. Tracking (Agent Tracking Panel)

Activates and displays information about selected agents.

### 4. Profiler (Profiler Panel)

Activates and displays profile information about the GPL code.

### 5. Data Sets (Data Set Panel)

Displays the currently loaded data set.

## Practical Usage Tips

- Use `$DebugOut(id, "message", variable)` in GPL code to print debug output
- The debugger is invaluable for verifying that effector functions are being called correctly
- Breakpoints on specific units help trace AI decision-making in real time
- The Call Stack view shows the full chain of GPL function calls leading to the current point
- The Profiler can identify GPL functions that run too frequently and may cause lag
