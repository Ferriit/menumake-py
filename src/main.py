#!/usr/bin/env python3

import curses
import os
from os.path import isfile
import sys
import json

def resolvepath(menu, path):
    if not path or path == "/":
        return menu

    parts = [p for p in path.split("/") if p]

    curr = menu
    for part in parts:
        if part in curr:
            value = curr[part]
            if isinstance(value, list):
                found_submenu = None
                for item in value:
                    if isinstance(item, dict):
                        found_submenu = item
                        break
                if found_submenu is not None:
                    curr = found_submenu
                else:
                    curr = value
            elif isinstance(value, dict):
                curr = value
            else:
                return None
        else:
            return None

    return curr

def saveconfig(menu, command, is_makefile):
    max_index = 0
    def find_max_index(m):
        nonlocal max_index
        for val in m.values():
            if isinstance(val, list):
                if len(val) >= 3 and isinstance(val[0], (bool, int)) and isinstance(val[2], int):
                    max_index = max(max_index, val[2])
                elif len(val) == 1 and isinstance(val[0], dict):
                    find_max_index(val[0])
            elif isinstance(val, dict):
                find_max_index(val)
    find_max_index(menu)

    outputs = [""] * (max_index + 1)

    def walk(m):
        for val in m.values():
            if isinstance(val, list) and len(val) == 1 and isinstance(val[0], dict):
                walk(val[0])
                continue

            if isinstance(val, list) and len(val) >= 3:
                idx = val[2]
                if isinstance(val[0], bool):
                    if val[0]:
                        outputs[idx] += val[1] + " "
                elif isinstance(val[0], int):
                    outputs[idx] += val[1].replace("$", str(val[0])) + " "

            elif isinstance(val, dict):
                walk(val)

    walk(menu)

    final_command = command
    for i, out in enumerate(outputs):
        if not is_makefile:
            # Assume shell script
            final_command = f"export MENUMAKE_OPTIONS_{i}='{out.strip()}'\n{final_command}"

        else:
            # Assume makefile
            final_command = f"MENUMAKE_OPTIONS_{i} := '{out.strip()}'\n{final_command}"

    with open(".makemenu.make" if is_makefile else ".makemenu.sh", "w") as f:
        f.write(final_command)

def main(stdscr):
    curses.start_color()
    curses.use_default_colors()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(True)

    stdscr.nodelay(True)

    selectedthing = 0

    # Example menu data structure in makemenu.json:
    # {
    #     "command": "gcc main.c -o main ",
    #     "menu": {
    #         "Toggle 1": [False, "-DToggle1"], 
    #         "Toggle 2": [False, "-DToggle2"], 
    #         "Toggle 3": [False, "-DToggle3"],
    #         "Submenu": [
    #             {
    #                 "Subtoggle 1": [False, "-DSubtoggle1"], 
    #                 "Subtoggle 2": [False, "-DSubtoggle2"], 
    #                 "Subtoggle 3": [False, "-DSubtoggle3"]
    #             }
    #         ],
    #         "Number": [0, "-DNumber=$"]
    #     } // $ = placeholder for number value
    # }

    menudata = json.loads(open("menumake.json").read())
    menu = menudata["menu"]
    command = open(menudata["command"]).read()

    is_makefile = menudata["command"] == "Makefile"

    rows, col = stdscr.getmaxyx();

    path = "/"

    currmenu = menu
        
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    stdscr.bkgd(" ", curses.color_pair(1))
    stdscr.clear()

    def clear():
        for y in range(5, rows - 5):
            stdscr.addstr(y, 9, "║" + " " * (col - 20) + "║", curses.color_pair(1))
            stdscr.addstr(y, 10, " " * (col - 20), curses.color_pair(2))

        stdscr.addstr(4, 9, "╔" + "═" * (col - 20) + "╗", curses.color_pair(1))
        stdscr.addstr(y + 1, 9, "╚" + "═" * (col - 20) + "╝", curses.color_pair(1))

    def drawcurrmenu():
        msg = "Menu"
        stdscr.addstr(4, (col - len(msg)) // 2, msg, curses.color_pair(2))

        msg = "Press ESC to save and exit"
        stdscr.addstr(0, 0, msg, curses.color_pair(2))

        # Determine visible area
        top = 5
        bottom = rows - 6
        visible_lines = bottom - top + 1

        global scroll_offset
        num_options = len(currmenu)
        # Adjust scroll_offset if selectedthing is outside the current view
        if selectedthing < scroll_offset:
            scroll_offset = selectedthing
        elif selectedthing >= scroll_offset + visible_lines:
            scroll_offset = selectedthing - visible_lines + 1

        cursX, cursY = 0, 0

        for i, (option, value) in enumerate(currmenu.items()):
            line_num = i - scroll_offset
            if line_num < 0 or line_num >= visible_lines:
                continue  # Skip lines outside visible window

            if type(value[0]) == bool:
                marker = '[*]' if value[0] else '[ ]'
            elif type(value[0]) == int:
                marker = f"[{value[0]}]"
            elif type(value[0]) == dict:
                marker = "->"
            else:
                marker = str(value[0])

            # Display the path (if needed)
            stdscr.addstr(top + line_num, 10, path, curses.color_pair(2))

            if i == selectedthing:
                cursX, cursY = 10, top + line_num
                stdscr.addstr(top + line_num, 10, f"*{option} {marker}", curses.color_pair(3))
            else:
                stdscr.addstr(top + line_num, 10, f"-{option} {marker}", curses.color_pair(2))

        stdscr.move(cursY, cursX)

    while True:
        ch = stdscr.getch()

        #stdscr.addstr(0, 0, f"Key: {str(ch)}   ", curses.color_pair(2))

        clear()
        drawcurrmenu()

        if ch == curses.KEY_UP or ch == ord("k") or ch == ord("w"):
            selectedthing = (selectedthing - 1) % len(list(currmenu))

        elif ch == curses.KEY_DOWN or ch == ord("j") or ch == ord("s"):
            selectedthing = (selectedthing + 1) % len(list(currmenu))

        # Handle toggles
        elif (ch == curses.KEY_ENTER or ch == 10 or ch == 13 or ch == ord(" ")) and type(currmenu[list(currmenu)[selectedthing]][0]) == bool:
            currmenu[list(currmenu)[selectedthing]][0] = not currmenu[list(currmenu)[selectedthing]][0]

        # Handle submenus
        elif (ch == curses.KEY_ENTER or ch == 10 or ch == 13) and type(currmenu[list(currmenu)[selectedthing]][0]) == dict:
            path += list(currmenu)[selectedthing] + "/"
            currmenu = resolvepath(menu, path)
            selectedthing = 0

        # Handle going back from submenus
        elif ch == curses.KEY_BACKSPACE or ch == 127 or ch == 8:
            if path == "/":
                saveconfig(menu, command, is_makefile)
                break
            path = "/".join(path.split("/")[:-2]) + "/"
            currmenu = resolvepath(menu, path)
            selectedthing = 0
        
        # Handle increments/decrements
        elif (ch == curses.KEY_RIGHT or ch == ord("l") or ch == ord("d")) and type(currmenu[list(currmenu)[selectedthing]][0]) == int:
            currmenu[list(currmenu)[selectedthing]][0] += 1
        
        elif (ch == curses.KEY_LEFT or ch == ord("h") or ch == ord("a")) and type(currmenu[list(currmenu)[selectedthing]][0]) == int:
            currmenu[list(currmenu)[selectedthing]][0] -= 1

        stdscr.refresh()
        if ch == 27:
            saveconfig(menu, command, is_makefile)
            break


if __name__ == "__main__":
    openmenu = True
    build = False
    if len(sys.argv) > 1:
        if "build" in sys.argv:
            openmenu = False
            build = True
        
        if "run" in sys.argv:
            openmenu = True
    
    if openmenu:
        curses.wrapper(main)

    if build:
        if os.path.isfile(".makemenu.sh"):
            os.system("sh .makemenu.sh")
            os.remove(".makemenu.sh")

        elif os.path.isfile(".makemenu.make"):
            os.system("make -f .makemenu.make")
            os.remove(".makemenu.make")

        else:
            print("No menumake build file exists for either shell or make. Run menumake to generate it")
