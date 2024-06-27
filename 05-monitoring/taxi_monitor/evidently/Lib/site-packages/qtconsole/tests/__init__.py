
import os
import sys

no_display = (sys.platform not in ('darwin', 'win32') and
              os.environ.get('DISPLAY', '') == '')
