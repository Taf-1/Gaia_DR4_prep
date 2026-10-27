import logging 

class SimulationRun:
    def __init__(self, logger: logging.Logger, full_query_csv: str, vari_target_csv: str):
        self.logger = logger
        self.full_query_csv = full_query_csv
        self.vari_target_csv = vari_target_csv