from Logger import Logger
from LogManager import LogManager

# single logger test
# logger = LogManager()
# logTester = logger.start('LoggerTester')
# logTester.debug("This is a debug message")
# logTester.info("This is an info message")
# logTester.error("This is an error message")
# logger.stop('LoggerTester')

# multiple logger test
logger = LogManager('LoggerConfig.json')
serviceAlogger = logger.start('ServiceA')
serviceBlogger = logger.start('ServiceB')
serviceClogger = logger.start('ServiceC')

serviceAlogger.debug("Service A debug message")
serviceAlogger.info("Service A info message")
serviceAlogger.error("Service A error message")
serviceBlogger.debug("Service B debug message")
serviceBlogger.info("Service B info message")
serviceBlogger.error("Service B error message")
serviceClogger.debug("Service C debug message")
serviceClogger.info("Service C info message")
serviceClogger.error("Service C error message")

logger.stop('ServiceA')
logger.stop('ServiceB')
logger.stop('ServiceC')

# logger.stopAll()  # Stop all loggers if needed
