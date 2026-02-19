# menumake-py
A simple build program that supports menus

## !DISCLAIMER!
### Do NOT use this for actual projects that require value checking for integers or projects that require multi-line compilation as this DOES NOT support such compilation and is incredibly unstable without value checking!

 * To run the configuration, run `makemenu`.
 * To run the generated shell script, run `makemenu build`. This skips the menu.
 * Tp run the configuration and also run the generated shell script, run `makemenu run build`.


### Syntax:
 * The syntax is in JSON and has two fields at the top. "command" for a path to a build scrpt and "menu" for the menu layout.
 * This supports Submenus, Integers and Booleans.
 * The options get added in the build script where there's a "$MENUMAKE_OPTIONS_#" string where "#" is the last argument in the list for a menu entry.

#### Boolean Syntax:
 * `"Name", [false, "COMPILATION FLAG", 0]`. The compilation flag gets added to the compilation command if it has been set to True.

#### Integer Syntax:
 * `"Name", [0, "COMPILATIONFLAG=$", 0]`. The $ gets substituted with the value set in the menu.

#### Submenu Syntax:
 * `"Name": [{}]`. This shows up as "Name" in the menu and allows the user to change everything inside the submenu. The syntax inside the curly braces for a submenu is the same as that of the main menu
