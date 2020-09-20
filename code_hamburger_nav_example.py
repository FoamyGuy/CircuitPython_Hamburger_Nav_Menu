import time
import board
import microcontroller
import displayio
import busio
import neopixel
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from adafruit_button import Button
import adafruit_touchscreen
import adafruit_imageload
import terminalio

class TileGridButton(displayio.TileGrid):
    def contains(self, touch_point):
        if self.x < touch_point[0] and self.x + width > touch_point[0]:
            if self.y < touch_point[1] and self.y + height > touch_point[1]:
                return True
        return False

NAV_VISIBLE = False

CLICK_COOLDOWN = 0.5

currently_showing_layer = None

display = board.DISPLAY
display.rotation = 270

# Touchscreen setup
# ------Rotate 270:
screen_width = 240
screen_height = 320
ts = adafruit_touchscreen.Touchscreen(board.TOUCH_YD, board.TOUCH_YU,
                                      board.TOUCH_XR, board.TOUCH_XL,
                                      calibration=((5200, 59000),
                                                   (5800, 57000)),
                                      size=(screen_width, screen_height))


# ------------- Display Groups ------------- #
splash = displayio.Group(max_size=15)  # The Main Display Group
view1 = displayio.Group(max_size=15)  # Group for View 1 objects
view2 = displayio.Group(max_size=15)  # Group for View 2 objects
view3 = displayio.Group(max_size=15)  # Group for View 3 objects

MENU_ITEMS = [
    "Page 1",
    "Page 2",
    "Page 3"
]

MENU_VIEWS = [
    view1,
    view2,
    view3
]

MENU_BTNS = []


def hideLayer(hide_target):
    try:
        splash.remove(hide_target)
    except ValueError:
        pass

def showLayer(show_target):
    try:
        time.sleep(0.1)
        splash.append(show_target)
    except ValueError:
        pass


# Set the font and preload letters
font = bitmap_font.load_font("/fonts/Helvetica-Bold-16.bdf")
font.load_glyphs(b'abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890- ()')

# Text Label Objects
view1_label = Label(font, text="Text Wondow 1", color=0xE39300, max_glyphs=200)
view1_label.x = 40
view1_label.y = 40
view1.append(view1_label)

# Text Label Objects
view2_label = Label(font, text="Text Wondow 2", color=0x2293E3, max_glyphs=200)
view2_label.x = 80
view2_label.y = 80
view2.append(view2_label)

# Text Label Objects
view3_label = Label(font, text="Text Wondow 3", color=0x00E343, max_glyphs=200)
view3_label.x = 80
view3_label.y = 120
view3.append(view3_label)

currently_showing_layer = view3
showLayer(view3)

hamburger_icon, palette = adafruit_imageload.load("/hamburger_icon.bmp",
                                         bitmap=displayio.Bitmap,
                                         palette=displayio.Palette)

palette.make_transparent(0)

width = hamburger_icon.width
height = hamburger_icon.height

# Create a TileGrid to hold the bitmap
icon_btn = TileGridButton(hamburger_icon, pixel_shader=palette)

splash.append(icon_btn)
display.show(splash)

def create_btn(text):
    # Make the button
    button = Button(
        x=0,
        y=0,
        width=100,
        height=30,
        fill_color=0xCCCCCC,
        outline_color=0x999999,
        label=text,
        label_font=terminalio.FONT,
        label_color=0x000000,
    )
    return button

nav_menu_group = displayio.Group(max_size=len(MENU_ITEMS) + 2)
nav_menu_group.x = 0
nav_menu_group.y = 0


for i, item in enumerate(MENU_ITEMS):
    print(item)
    btn = create_btn(item)
    btn.y = btn.height * i
    btn.group.y = btn.height * i
    print(btn.y)

    MENU_BTNS.append(btn)
    nav_menu_group.append(btn.group)

prev_click_time = 0
while True:
    p = ts.touch_point
    if p and time.monotonic() > prev_click_time + CLICK_COOLDOWN:
        print(p)
        if not NAV_VISIBLE:
            if icon_btn.contains(p):
                prev_click_time = time.monotonic()
                showLayer(nav_menu_group)
                NAV_VISIBLE = True
                print("CLICKED!")
        else:
            for i, btn in enumerate(MENU_BTNS):
                if btn.contains(p):
                    prev_click_time = time.monotonic()
                    print("Clicked {}".format(MENU_ITEMS[i]))
                    NAV_VISIBLE = False
                    hideLayer(currently_showing_layer)
                    currently_showing_layer = MENU_VIEWS[i]
                    showLayer(MENU_VIEWS[i])
                    hideLayer(nav_menu_group)
