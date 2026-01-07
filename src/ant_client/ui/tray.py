import sys
import os
import threading
import webbrowser
from PIL import Image, ImageDraw
import pystray

class AntTray:
    def __init__(self, on_exit_callback, dashboard=None):
        self.on_exit_callback = on_exit_callback
        self.dashboard = dashboard
        self.icon = None
        self.running = True

    def create_image(self, width=64, height=64):
        image = Image.new('RGB', (width, height), (30, 41, 59)) # Slate-800
        dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill=(59, 130, 246)) # Blue-500
        return image

    def on_open_dashboard(self, icon, item):
        if self.dashboard:
            self.dashboard.show()
        else:
            webbrowser.open("http://localhost:3000/admin/deepsync")

    def on_exit(self, icon, item):
        import ctypes
        result = ctypes.windll.user32.MessageBoxW(0, "Are you sure you want to stop the Monewment Ant Client?", "Confirm Exit", 0x01 | 0x30 | 0x1000)
        
        if result == 1: # IDOK
            self.running = False
            icon.stop()
            if self.on_exit_callback:
                self.on_exit_callback()

    def run(self):
        icon_path = os.path.join(os.path.dirname(__file__), "../../../assets/icon.ico")
        if os.path.exists(icon_path):
             image = Image.open(icon_path)
        else:
             image = self.create_image()

        menu = pystray.Menu(
            pystray.MenuItem("Monewment Ant (Active)", lambda i, it: None, enabled=False),
            pystray.MenuItem("Open Dashboard", self.on_open_dashboard, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.on_exit)
        )

        self.icon = pystray.Icon("MonewmentAnt", image, "Monewment Ant Client", menu)
        self.icon.run()
