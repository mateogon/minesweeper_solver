import subprocess
def window_to_foreground(title):
    cmd = f"wmctrl -a '{title}'"
    result = subprocess.run(cmd, shell=True)
    
def get_window_dimensions(title):
    # get the window ID using wmctrl
    cmd = f"wmctrl -l | grep '{title}' | awk '{{print $1}}'"
    result = subprocess.run(cmd, shell=True, capture_output=True)
    window_id = result.stdout.decode().strip()
    # get the window geometry using xwininfo
    cmd = f"xwininfo -id {window_id}"
    result = subprocess.run(cmd, shell=True, capture_output=True)
    geometry = result.stdout.decode()
    # parse the geometry string to get the dimensions
    lines = geometry.split('\n')
    width = height = x = y = None
    for line in lines:
        if line.startswith("  Width:"):
            width = int(line.split()[1])
        elif line.startswith("  Height:"):
            height = int(line.split()[1])
        elif line.startswith("  Absolute upper-left X:"):
            x = int(line.split()[3])
        elif line.startswith("  Absolute upper-left Y:"):
            y = int(line.split()[3])
    return (x, y, width, height)
