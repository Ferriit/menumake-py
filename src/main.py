#!/usr/bin/env python3

import curses
import os
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

def saveconfig(menu, command, depth=0):
    output = ""

    for i, (option, value) in enumerate(menu.items()):
        if type(value[0]) == bool:
            if value[0]:
                output += f"{value[1]} "

        elif type(value[0]) == int:
            output += value[1].replace("$", str(value[0])) + " "

        elif type(value[0]) == dict:
            # Assume submenu. First element is dict of options
            output += saveconfig(value[0], command, depth + 1)
    
    if depth != 0:
        return output
    open(".makemenu.sh", "w").write(command.replace("$MENUMAKE_OPTIONS", output))

def main(stdscr):
    curses.start_color()
    curses.use_default_colors()
    curses.noecho()
    curses.cbreak()
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
    command = menudata["command"]

    rows, col = stdscr.getmaxyx();

    path = "/"

    currmenu = menu

    curses.init_pair(1, 16, curses.COLOR_BLUE)
    curses.init_pair(2, 16, 255)
    curses.init_pair(3, 255, 240)

    stdscr.bkgd(" ", curses.color_pair(1))
    stdscr.clear()

    def clear():
        for y in range(5, rows - 5):
            stdscr.addstr(y, 10, " " * (col - 20), curses.color_pair(2))

    def drawcurrmenu():
        msg = "Menu"
        stdscr.addstr(4, (col - len(msg)) // 2, msg, curses.color_pair(2))

        msg = "Press ESC to save and exit"
        stdscr.addstr(0, 0, msg, curses.color_pair(2))

        cursX, cursY = 0, 0

        for i, (option, value) in enumerate(currmenu.items()):
            if type(value[0]) == bool:
                marker = '[*]' if value[0] else '[ ]'

            elif type(value[0]) == int:
                marker = f"[{value[0]}]"
            elif type(value[0]) == dict:
                # Assume submenu. First element is options dict
                marker = f"->"

            else:
                marker = str(value[0])
            
            stdscr.addstr(5, 10, path, curses.color_pair(2))

            if i == selectedthing:
                cursX, cursY = 10, 5 + i + 1
                stdscr.addstr(5 + i + 1, 10, f" {option} {marker}", curses.color_pair(3))
            else:
                stdscr.addstr(5 + i + 1, 10, f" {option} {marker}", curses.color_pair(2))

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
                saveconfig(menu, command)
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
            saveconfig(menu, command)
            break


if __name__ == "__main__":
    openmenu = True
    if len(sys.argv) > 1:
        if sys.argv[1] == "build":
            openmenu = False
            os.system("sh .makemenu.sh")

    if openmenu:
        curses.wrapper(main)
