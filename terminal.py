import sys
import tty
import termios

isTerminal = True

def getch():
    global isTerminal

    if isTerminal:
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
        except:
            isTerminal = False
            return getch()
    else:
        while True:
            line = sys.stdin.readline()
            if len(line) > 0:
                return line[0]
