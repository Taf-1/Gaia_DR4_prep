import logging 

class Simulate:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def run_simulation(self) -> None:
        self.logger.info("Starting simulation...")

        self.logger.info("Simulation completed.")