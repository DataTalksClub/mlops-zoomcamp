"""Lancement : python -m agents.reliability (depuis prototype/)."""
import logging

from agents.reliability.agent import ReliabilityAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
ReliabilityAgent().run_forever()
