import subprocess
from Xlib import X, display, Xutil,XK
from Xlib.ext.xtest import fake_input
import Xlib
def window_to_foreground_similar(title): #not exact name
    cmd = f"wmctrl -a '{title}'"
    result = subprocess.run(cmd, shell=True)
    
def get_window_dimensions_similar(title): #not exact name
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

def get_window_id(title):
    # Get the window ID using wmctrl
    cmd = f"wmctrl -l | awk '{{if ($0 ~ /{title}$/) print $1}}'"
    result = subprocess.run(cmd, shell=True, capture_output=True)
    window_id = result.stdout.decode().strip()
    return window_id if window_id else None

def get_window_dimensions(window_id):
    if not window_id:
        return None

    # Get the window geometry using xwininfo
    cmd = f"xwininfo -id {window_id}"
    result = subprocess.run(cmd, shell=True, capture_output=True)
    geometry = result.stdout.decode()

    # Parse the geometry string to get the dimensions
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

def window_to_foreground(title):
    # Bring the window to the foreground using wmctrl
    cmd = f"wmctrl -F -a '{title}'"
    result = subprocess.run(cmd, shell=True)
    
    
def send_key_to_window(window_id, key):
    d = display.Display()
    root = d.screen().root
    keysym = XK.string_to_keysym(key)
    # Create a key event
    keycode = d.keysym_to_keycode(keysym)
    key_event = Xlib.protocol.event.KeyPress(
        time=X.CurrentTime, root=root, window=window_id,
        child=X.NONE, root_x=0, root_y=0, event_x=0, event_y=0,
        same_screen=0, state=X.Mod1Mask, detail=keycode
    )

    # Send the key press event
    root.send_event(key_event, event_mask=X.KeyPressMask)
    d.sync()

    # Create a key release event
    key_event = Xlib.protocol.event.KeyRelease(
        time=X.CurrentTime, root=root, window=window_id,
        child=X.NONE, root_x=0, root_y=0, event_x=0, event_y=0,
        same_screen=0, state=X.Mod1Mask, detail=keycode
    )

    # Send the key release event
    root.send_event(key_event, event_mask=X.KeyReleaseMask)
    d.sync()

def send_click(x, y, window_id, button):
    d = display.Display()
    root = d.screen().root

    # Create a button press event
    press_event = Xlib.protocol.event.ButtonPress(
    time=Xlib.X.CurrentTime, root=root, window=root,
    same_screen=1, button=button, child=Xlib.X.NONE,
    root_x=0, root_y=0, event_x=x, event_y=y,  # set event_x and event_y to out-of-bounds values
    state=0, detail=1
)
    # Create a button release event
    release_event = Xlib.protocol.event.ButtonRelease(
        time=X.CurrentTime, root=root, window=window_id,
        child=X.NONE, root_x=0, root_y=0, event_x=x, event_y=y,
        same_screen=0, detail=button,state=0
    )

    # Send the button press event
    #root.send_event(press_event, event_mask=X.ButtonPressMask)
    root.send_event(press_event, propagate=Xlib.X.SubstructureRedirectMask|Xlib.X.SubstructureNotifyMask)
    d.sync()

    # Send the button release event
    #root.send_event(release_event, event_mask=X.ButtonReleaseMask)
    root.send_event(release_event, propagate=Xlib.X.SubstructureRedirectMask|Xlib.X.SubstructureNotifyMask)
    d.sync()
def send_mouse_click(x, y, button, window_id=None):
    d = display.Display()

    if window_id:
        window = d.create_resource_object('window', window_id)
    else:
        window = d.screen().root

    # Move the mouse to the specified coordinates
    window.warp_pointer(x, y)
    d.sync()

     # Click the mouse
    #window.grab_pointer(True, X.ButtonPressMask | X.ButtonReleaseMask, X.GrabModeAsync, X.GrabModeAsync, 0, 0, X.NONE)
    d.sync()
    fake_input(d,X.ButtonPress, button)
    d.sync()
    fake_input(d,X.ButtonRelease, button)
    d.sync()

    # Release the mouse
    #window.ungrab_pointer(X.CurrentTime)
    d.sync()

def move_mouse(x,y):
    d = display.Display()
    root = d.screen().root
    root.warp_pointer(x,y)
    d.sync()
    
def click(d, x, y, button):
    
    # Move the pointer to the specified position
    fake_input(d, X.MotionNotify, x=x, y=y)

    # Send a press event
    fake_input(d, X.ButtonPress, button)

    # Send a release event
    fake_input(d, X.ButtonRelease, button)

    # Make sure the events are flushed to the server
    d.sync()