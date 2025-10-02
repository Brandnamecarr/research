from Logger import Logger
from LogManager import LogManager

logger = LogManager()
logger.start('LoggerTester')
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.error("This is an error message")
logger.stop('LoggerTester')