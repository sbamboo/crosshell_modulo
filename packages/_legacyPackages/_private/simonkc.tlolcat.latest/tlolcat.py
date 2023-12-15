import random

# ANSI color codes and their RGB equivalents
ANSI_COLORS = [
    (255, 0, 0),      # Red
    (0, 255, 0),      # Green
    (255, 255, 0),    # Yellow
    (0, 0, 255),      # Blue
    (255, 0, 255),    # Magenta
    (0, 255, 255),    # Cyan
    (255, 85, 85),    # Red (Bright)
    (85, 255, 85),    # Green (Bright)
    (255, 255, 85),   # Yellow (Bright)
    (85, 85, 255),    # Blue (Bright)
    (255, 85, 255),   # Magenta (Bright)
    (85, 255, 255),   # Cyan (Bright)
    (255, 128, 0),    # Orange
    (128, 0, 128),    # Purple
    (0, 128, 255),    # Light Blue
    (128, 128, 0),    # Yellow-Green
]

RESET_COLOR = "\033[0m"

def generate_gradient(start_color, end_color, num_steps):
    """
    Generate a gradient of RGB ANSI codes between two colors.
    """
    start_r, start_g, start_b = start_color
    end_r, end_g, end_b = end_color
    step_r = (end_r - start_r) / num_steps
    step_g = (end_g - start_g) / num_steps
    step_b = (end_b - start_b) / num_steps

    gradient = []
    for i in range(num_steps):
        r = int(start_r + i * step_r)
        g = int(start_g + i * step_g)
        b = int(start_b + i * step_b)
        gradient.append(f"\033[38;2;{r};{g};{b}m")
    
    return gradient

def lolcat(sargv):
    start_color = random.choice(ANSI_COLORS)
    end_color = random.choice(ANSI_COLORS)
    num_steps = len(sargv)

    gradient = generate_gradient(start_color, end_color, num_steps)
    colored_text = ""

    for i, char in enumerate(sargv):
        if char.isspace():
            colored_text += char
        else:
            color_code = gradient[i % num_steps]
            colored_text += f"{color_code}{char}"
    
    colored_text += RESET_COLOR  # Reset color at the end
    return colored_text

grad = lolcat(sargv)

print(grad)