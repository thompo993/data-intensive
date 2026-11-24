import glob, pandas as pd
df = pd.concat(pd.read_parquet(f) for f in glob.glob("data/*.parquet"))
fire = df["fire_active_max"] > 0
print(f"{fire.mean():.3%} of cell-days; {df.loc[fire, 'window_start'].dt.date.nunique()} days with any fire")