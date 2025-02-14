import os
import logging
import sys


class ColorHandler(logging.StreamHandler):
	# https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
	GRAY8 = "38;5;8"
	PURPLE = "35"
	ORANGE = "33"
	RED = "31"
	WHITE = "0"

	def emit(self, record):
		# We don't use white for any logging, to help distinguish from user print statements
		level_color_map = {
			logging.DEBUG: self.GRAY8,
			logging.INFO: self.PURPLE,
			logging.WARNING: self.ORANGE,
			logging.ERROR: self.RED,
		}

		csi = f"{chr(27)}["  # control sequence introducer
		color = level_color_map.get(record.levelno, self.WHITE)

		self.stream.write(f"{csi}{color}m{record.msg}{csi}m\n\n")
		self.setStream(sys.stdout)


logger = logging.getLogger(__name__)
logger.setLevel(10)

# See https://no-color.org/
if not os.environ.get("NO_COLOR"):
	logging.getLogger(__name__).addHandler(ColorHandler())

file_handler = logging.FileHandler("vocabChecker.log", mode="a", encoding="utf-8")
logger.addHandler(file_handler)
# TODO logging print is delayed
