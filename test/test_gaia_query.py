from astroquery.gaia import Gaia
import pandas as pd

job = Gaia.launch_job_async("""
    SELECT TOP 50 c.source_id, c.best_class_name, c.best_class_score
    FROM gaiadr3.vari_classifier_result AS c
    JOIN gaiadr3.gaia_source AS g USING (source_id)
    WHERE g.has_epoch_photometry = 'True'
      AND c.best_class_score > 0.8
""")
labels = job.get_results().to_pandas()

frames = []
ids = labels["source_id"].tolist()
for i in range(0, len(ids), 50):
    data = Gaia.load_data(
        ids=ids[i:i+50],
        retrieval_type="EPOCH_PHOTOMETRY",
        data_release="Gaia DR3",
        data_structure="DATAMODEL_STANDARD",
        format="votable",
    )
    for key, tables in data.items():
        frames.append(tables[0].to_table().to_pandas())

lc = pd.concat(frames) 
lc.to_parquet("gaia_lightcurves.parquet")
labels.to_parquet("gaia_labels.parquet")