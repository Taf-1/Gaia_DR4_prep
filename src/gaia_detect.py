import pandas as pd
import numpy as np

class EB_detect:
    def __init__(self, lightcurve_file: str, sources_file: str) -> None:
        self.lightcurve_file = lightcurve_file
        self.sources_file = sources_file
        self.output_dir = output_dir

    def load_data(self) -> None:
        self.lightcurve_file_df = pd.read_parquet(self.lightcurve_file)
        self.sources_file_df = pd.read_parquet(self.sources_file)

    def lc_dips(self) -> None:
        eb = {
        }
        for i, row in self.sources_file_df.iterrows():
            source_id = row['source_id']
            source_lightcurve = self.lightcurve_file_df[self.lightcurve_file_df['source_id'] == source_id]
            # TODO: adjust based on file headers
            flux, flux_err, ts = source_lightcurve['flux'].values, source_lightcurve['flux_err'].values, source_lightcurve['ts'].values
            ratio = flux / np.median(flux)
            norm_flux = ratio / np.median(ratio)
            dropouts = np.where(norm_flux < 0.5)[0]
            # TODO: see confirmed eb lightcurves to see how many data points they have 
            n = 5 # arbitrary number of dropouts to consider a source as an eclipsing binary
            if len(dropouts) > n:
                eb[source_id] = {
                    'dropouts': dropouts,
                    'flux': flux,
                    'flux_err': flux_err,
                    'ts': ts,
                    'score': len(dropouts)
                }

    def missing_scans(self) -> None:
        # TODO: see what that would look like

class EB_stats:
    def __init__(self, lightcurve_file: str, sources_file: str, output_dir: str) -> None:
        self.lightcurve_file = lightcurve_file
        self.sources_file = sources_file
        self.output_dir = output_dir

    def sts(self) -> None:
        # TODO: statistical detection to improve the score of each eclipsing binary candidate
        