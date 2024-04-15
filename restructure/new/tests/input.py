import sys
import os

class Storage:
    def __init__(self):
        self.internal_string = ""

def get_char():
    import sys
    if sys.platform == 'win32':
        import msvcrt
        return msvcrt.getch().decode()

    else:  # For Unix-like systems
        import termios
        import tty
        import sys

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return char

def move_cursor_left():
    sys.stdout.write('\b')
    sys.stdout.flush()

def move_cursor_right():
    sys.stdout.write('\x1b[C')
    sys.stdout.flush()

def handle_backspace(input_string, cursor_pos):
    if cursor_pos > 0:
        input_string = input_string[:cursor_pos-1] + input_string[cursor_pos:]
        sys.stdout.write('\b \b' + input_string[cursor_pos-1:] + ' '*(len(input_string)-cursor_pos+1))
        sys.stdout.flush()
        cursor_pos -= 1
    return input_string, cursor_pos

def constructor(storage_instance):
    def custom_input(prompt=''):
        sys.stdout.write(prompt)
        sys.stdout.flush()

        input_string = ''
        cursor_pos = 0
        while True:
            char = get_char()

            if char != None:
                if char == '\r' or char == '\n':  # Enter key
                    # If Enter is pressed, return the input string
                    sys.stdout.write('\n')
                    sys.stdout.flush()
                    storage_instance.internal_string = input_string
                    return input_string

                elif char == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt

                elif char == '\x7f':  # Backspace
                    # Handle backspace
                    input_string, cursor_pos = handle_backspace(input_string, cursor_pos)

                else:
                    # Insert character at cursor position
                    input_string = input_string[:cursor_pos] + char + input_string[cursor_pos:]
                    sys.stdout.write(char + input_string[cursor_pos+1:] + '\b'*(len(input_string)-cursor_pos-1))
                    sys.stdout.flush()
                    cursor_pos += 1

    return custom_input

inst = Storage()

input = constructor(inst)

t = input("> ")

print(t)