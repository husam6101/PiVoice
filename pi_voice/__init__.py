import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s - %(asctime)s - %(filename)s > %(message)s')

# Create a logger
logger = logging.getLogger(__name__)
