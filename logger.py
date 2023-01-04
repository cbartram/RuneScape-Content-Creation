import sys
import logging
from datetime import date


formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Log to standard output
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
log.addHandler(handler)

# Also log to file to read and send in emails
fh = logging.FileHandler(f'logs/osrs_log_{date.today().strftime("%Y-%m-%d")}.log')
fh.setLevel(logging.DEBUG)
log.addHandler(fh)
