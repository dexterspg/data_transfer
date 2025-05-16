import logging

class LoggingUtil:

    @staticmethod
    def setup_logger(logger_name, file_name='app.log', console_level=logging.DEBUG, file_level=logging.INFO):
        logger = logging.getLogger(logger_name)

        # Create handlers
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(file_name)

        # Set logging level for handlers
        console_handler.setLevel(console_level)
        file_handler.setLevel(file_level)

        # Create formatters and add them to handlers
        console_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        console_handler.setFormatter(console_format)
        file_handler.setFormatter(file_format)

        # Add handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger
