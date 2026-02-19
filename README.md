# menumake-py
A simple build program that supports menus

 * To run the configuration, run `makemenu`.
 * To run the generated shell script, run `makemenu build`. This skips the menu.
 * To run the configuration and also run the generated shell script, run `makemenu run build`.


### Syntax:
 * The syntax is in a custom format and has one field at the top, "command" for a path to a build script or a Makefile
 * This supports Submenus, Integers and Booleans thus far.
 * The options get added in the build script or Makefile as variables named "$MENUMAKE\_OPTIONS\_#" string where "#" is the last argument in the list for a menu entry.

 - Type is the type of the entry (int, toggle)
 - Value is the default value of the entry (true, false or a number)
 - Index is the variable index the entry will replace (0 for MENUMAKE\_OPTIONS\_0, 1 for MENUMAKE\_OPTIONS\_1 etc. etc.)
 - Flags is a string with what will be added if the entry is true. If the entry is an int, it will replace "$" in the flag string with the value
 - (min / max) are optional for ints. Min is the lowest number and Max is the highest number. If they aren't provided, the int becomes unbound. Min always has to come before Max.
 - All definition parts of an entry are lowercase except for the label.
 - To define an entry, wrap a name in square brackets ("[" and "]"). Then add the necessary fields.
 - To define a submenu, write a name for it, then add a colon (":") at the end of the line. To put things in the submenu, indent them more than the submenu is indented.

#### Example:
```
# Command supports both shell scripts and Makefiles
command: "menumake_test.sh"

[Option 1]
type = "toggle"
value = "false"
# Replace MENUMAKE_OPTIONS_0
index = "0"
flags = "This is option 1."

[Option 2]
type = "toggle"
value = "true"
index = "0"
flags = "This is option 2."

Submenu:
	[Suboption 1]
	type = "toggle"
	value = "false"
	index = "0"
	flags = "This is suboption 1."

	[Suboption 2]
	type = "toggle"
	value = "true"
	index = "0"
	flags = "This is suboption 2."

[Option 3]
type = "int"
value = "0"
# Min must come before max
min = "0"
max = "10"
index = "0"
flags = "Option 3 is $."
```

