import sys
import logging
import argparse

from huey.consumer import Consumer
from huey.consumer_options import ConsumerConfig
from huey.consumer_options import OptionParserHandler
from huey.utils import load_class

import multiprocessing
from multiprocessing import freeze_support, Process

from app import app
from app import huey
from tasks import *  # Import tasks so they are registered with Huey instance.
from views import *  # Import views so they are registered with Flask app.
from waitress import serve

def consumer_main():
    # Set up logging for the "huey" namespace.
    logger = logging.getLogger('huey')
    config = ConsumerConfig()
    config.setup_logger(logger)

    consumer = huey.create_consumer(workers=1, periodic=False, backoff=1)
    consumer.run()

if __name__ == '__main__':
    freeze_support()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, help='Port of IO server.', default=11002)
    args = parser.parse_args()

    proc = Process(target=consumer_main)
    proc.start()

    # app.run(host='0.0.0.0', port=args.port)

    print(f'Running YeastMate IO backend server on port {args.port}. Press Ctrl-C to quit.')

    serve(app, host='0.0.0.0', port=args.port)

    print('Shutting down...')