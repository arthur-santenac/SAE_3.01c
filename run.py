import sys
import os
import webbrowser
from threading import Timer


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monApp.app import app

import monApp.views 

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(port=5000, debug=False)