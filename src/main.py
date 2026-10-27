from logger import Gaia_DR4_logger
from gaia_query import GaiaQuery
from simulation_run import SimulationRun
from plotting import SimulationPlotter
from pathlib import Path
import argparse
import os
import logging

def arg_parse() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Gaia DR4 Data Retrieval")
    p.add_argument("--stages", type=str, nargs='+', choices=["query", "sim", "plot"], default=["query", "sim", "plot"], 
                help="Stages to run: query, simulation, plotting - default is all stages")
    return p.parse_args()

if __name__ == "__main__":
    args = arg_parse()
    log_file = Path(__file__).resolve().parent.parent / 'logs' / 'gaia_dr4.log'
    logger_setup = Gaia_DR4_logger(stage_name="Gaia_DR4", log_file=log_file)
    logger = logger_setup.setup_logger()

    logger.info(f"Starting Gaia DR4 process with stages: {args.stages}")

    if "query" in args.stages:
        logger.info("Starting Gaia query stage...")
        gaia_query = GaiaQuery(gaia_logger=logger)
        gaia_query.full_query_csv()
        gaia_query.vari_target_query_csv()
        gaia_query.labelled_query_csv()
        logger.info("Gaia query stage completed.")

    if "sim" in args.stages:
        logger.info("Starting simulation stage...")
        simulation_run = SimulationRun(logger=logger, 
                                       full_query_csv="data/gaia_photometry.csv", 
                                       vari_target_csv="data/gaia_vari_target_photometry.csv")
        simulation_run.run_simulation()
        logger.info("Simulation stage completed.")

    if "plot" in args.stages:
        logger.info("Starting plotting stage...")
        simulation_plotter = SimulationPlotter(simulation=simulation_run.simulation)
        simulation_plotter.plot_results()
        logger.info("Plotting stage completed.")