from astroquery.gaia import Gaia
from pathlib import Path
import logging
from tqdm import tqdm
import time
from typing import List, Optional
import pandas as pd

class GaiaQuery:
    def __init__(self, gaia_logger: logging.Logger):
        self.logger = gaia_logger
        DATA_DIR = Path(__file__).resolve().parent.parent / "data"
        BATCH_SIZE = 50       
        MAX_RETRIES = 3
        RETRY_DELAY = 5
        self.DATA_DIR = DATA_DIR
        self.BATCH_SIZE = BATCH_SIZE
        self.MAX_RETRIES = MAX_RETRIES
 
    def _run_adql(self, query: str) -> pd.DataFrame:
        """Run an ADQL query on the Gaia archive and return a DataFrame."""
        self.logger.info("Executing query...")
        job = Gaia.launch_job_async(query)
        return job.get_results().to_pandas()
 
    def _fetch_epoch_photometry(self, ids: List[int], desc: str) -> Optional[pd.DataFrame]:
        """
        Download epoch photometry for a list of source_ids via DataLink
        (Gaia.load_data), in batches, and return one combined DataFrame.
 
        Note: epoch photometry is NOT available as an ADQL table
        (gaiadr3.epoch_photometry can't be queried with SELECT), so DataLink
        is the way to get it.
        """
        ids = [int(i) for i in ids]
        batches = [ids[i:i + self.BATCH_SIZE] for i in range(0, len(ids), self.BATCH_SIZE)]
 
        frames = []
        for batch in tqdm(batches, desc=desc, unit="batch"):
            for attempt in range(1, self.MAX_RETRIES + 1):
                try:
                    data = Gaia.load_data(
                        ids=batch,
                        retrieval_type="EPOCH_PHOTOMETRY",
                        data_release="Gaia DR3",
                        data_structure="DATAMODEL_STANDARD",
                        format="votable",
                    )
                    # load_data returns {filename: [votable, ...]}
                    for tables in data.values():
                        for t in tables:
                            frames.append(t.to_table().to_pandas())
                    break
                except Exception as e:
                    self.logger.warning(
                        f"Batch starting {batch[0]} failed (attempt {attempt}/{self.MAX_RETRIES}): {e}"
                    )
                    if attempt == self.MAX_RETRIES:
                        self.logger.error(f"Giving up on batch starting {batch[0]}")
                    else:
                        time.sleep(self.RETRY_DELAY)
 
        if not frames:
            return None
        return pd.concat(frames, ignore_index=True)
 
    def _save(self, lc: Optional[pd.DataFrame], meta: pd.DataFrame, stem: str) -> None:
        """Save light curves and source metadata/labels as Parquet."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        if lc is None or lc.empty:
            self.logger.warning("No epoch photometry data retrieved.")
            return
        lc_path = self.DATA_DIR / f"{stem}_lightcurves.parquet"
        meta_path = self.DATA_DIR / f"{stem}_sources.parquet"
        lc.to_parquet(lc_path)
        meta.to_parquet(meta_path)
        self.logger.info(f"Saved {len(lc)} light-curve rows to {lc_path}")
        self.logger.info(f"Saved {len(meta)} sources to {meta_path}")


    def full_query_csv(self) -> None:
        """Small test sample: any sources with epoch photometry."""
        self.logger.info("Starting Gaia query...")
        sources = self._run_adql("""
            SELECT TOP 500 source_id, phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag,
                   phot_g_n_obs, ra, dec
            FROM gaiadr3.gaia_source
            WHERE phot_g_mean_mag BETWEEN 15 AND 19.5
            AND dec < 0
            AND has_epoch_photometry = 'True'
        """)
        self.logger.info(f"Retrieved {len(sources)} source IDs. Fetching epoch photometry...")
        lc = self._fetch_epoch_photometry(sources["source_id"].tolist(),
                                          desc="Fetching epoch photometry")
        self._save(lc, sources, "gaia_photometry")
 
    def vari_target_query_csv(self) -> None:
        """Variable sources from gaia_source, with their epoch photometry."""
        self.logger.info("Starting Gaia variable target query...")
        sources = self._run_adql("""
            SELECT TOP 500 source_id, phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag,
                   phot_g_n_obs, ra, dec
            FROM gaiadr3.gaia_source
            WHERE phot_g_mean_mag BETWEEN 15 AND 19.5
            AND dec < 0
            AND random_index < 5000000
            AND phot_variable_flag = 'VARIABLE'
            AND has_epoch_photometry = 'True'
        """)
        self.logger.info(f"Retrieved {len(sources)} variable source IDs. Fetching epoch photometry...")
        lc = self._fetch_epoch_photometry(sources["source_id"].tolist(),
                                          desc="Fetching variable target epoch photometry")
        self._save(lc, sources, "gaia_vari_target")
 
    def labelled_query(self, n: int = 5000, min_score: float = 0.8) -> None:
        """Classified variables (labels for ML) with their epoch photometry."""
        self.logger.info("Starting Gaia labelled variable query...")
        labels = self._run_adql(f"""
            SELECT TOP {int(n)} c.source_id, c.best_class_name, c.best_class_score,
                   g.phot_g_mean_mag, g.phot_bp_mean_mag, g.phot_rp_mean_mag, g.ra, g.dec
            FROM gaiadr3.vari_classifier_result AS c
            JOIN gaiadr3.gaia_source AS g USING (source_id)
            WHERE g.has_epoch_photometry = 'True'
            AND c.best_class_score > {float(min_score)}
        """)
        self.logger.info(f"Retrieved {len(labels)} labelled sources. Fetching epoch photometry...")
        lc = self._fetch_epoch_photometry(labels["source_id"].tolist(),
                                          desc="Fetching labelled epoch photometry")
        self._save(lc, labels, "gaia_labelled")