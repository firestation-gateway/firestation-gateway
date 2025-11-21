import logging
import sys
import time
from pathlib import Path

import click
import yaml
from pyee import EventEmitter

import firestation_gateway

from .consumers import get_consumer
from .producers import get_producer

CONFIG_EXAMPLE_FILE = "config.example.yaml"


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s|%(threadName)s] %(message)s",
    )


def consumer_setup(config, emitter):
    consumers = []
    for consumer_cfg in config["consumers"]:
        cls = get_consumer(consumer_cfg["type"])
        if not cls:
            logging.warning("Consumer '%s' not exists.", consumer_cfg["type"])
            continue

        consumer = cls(
            name=consumer_cfg["name"],
            emitter=emitter,
            events_config=consumer_cfg["events"],
            config=consumer_cfg["params"],
        )
        consumers.append(consumer)
    return consumers


def producer_setup(config, emitter):
    producers = []
    for producer_cfg in config["producers"]:
        cls = get_producer(producer_cfg["type"])
        if not cls:
            logging.warning("Producer '%s' not exists.", producer_cfg["type"])
            continue
        producer = cls(
            name=producer_cfg["name"],
            emitter=emitter,
            events_config=producer_cfg["events"],
            config=producer_cfg["params"],
        )
        producers.append(producer)
    return producers


@click.command()
# @click.option("--start", help="Start Firestation-Gateway", is_flag=True)
@click.option(
    "--config", help="Specify a configuration file", default="config.yaml"
)
@click.option(
    "--generate-config",
    help="Output a example configuration file",
    is_flag=True,
)
def main(config, generate_config):
    if generate_config:
        # Output config example and exits
        script_path = Path(__file__)
        script_dir = script_path.parent
        data_file = script_dir / CONFIG_EXAMPLE_FILE
        with open(data_file, "r", encoding="utf-8") as f:
            print(f.read())
        sys.exit(0)

    setup_logging()
    if Path(config).is_file():
        config_dict = load_config(config)
    else:
        logging.error("config file: '%s' not exists!", config)
        sys.exit(1)

    logging.info(
        "Start Firestation-Gateway v%s", firestation_gateway.__version__
    )
    logging.debug("Use config: %s", config)
    emitter = EventEmitter()

    consumers = consumer_setup(config_dict, emitter)
    producers = producer_setup(config_dict, emitter)

    # Start Threads
    for p in producers:
        p.start()
    for c in consumers:
        c.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("KeyboardInt...")

    # Stop Threads
    for p in producers:
        p.stop()
        p.join()
    for c in consumers:
        c.stop()
        c.join()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
