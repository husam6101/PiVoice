import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s in OPERATORS @ %(asctime)s > %(message)s')

# Create a logger
logger = logging.getLogger(__name__)
