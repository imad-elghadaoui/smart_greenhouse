import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/imad/smart_greenhouse_ws/install/greenhouse_sensors'
