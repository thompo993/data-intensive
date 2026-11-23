import glob 
import sys 
import pandas as pd 
from bokeh.io import save 
from bokeh.models import ColumnDataSource, DataTable, TableColumn, NumberFormatter
from bokeh.resources import INLINE

data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
out_file = sys.argv[2] if len(sys.argv) > 1 else "data_table.html"

files = sorted(glob.glob(f"{data_dir}/*.parquet"))
if not files: 
        raise SystemExit(f"no parquet files found in: '{data_dir}'!!")

df = pd.concat((pd.read_parquet(f) for f in files), ignore_index=True)
df = df.sort_values("window_start").reset_index(drop=True)

df["window_start"] = df["window_start"].dt.strftime("%Y-%m-%dT%H:%M:%S")

columns = [] 

for c in df.columns:
    if c == "window_start":
        columns.append(TableColumn(field=c, title=c, width=140))
    else: 
        columns.append(TableColumn(field=c, title=c, width=140, formatter=NumberFormatter(format="0.000")))

table = DataTable(
     source=ColumnDataSource(df),
     columns=columns,
     sortable=True,
     index_position=None,
     width=1400, 
     height=600
)

save(table, filename=out_file, resources=INLINE, title="GB Wildfire Prediction Data Table")
print(f"Table Saved to {out_file} | {len(df)} X {len(df.columns)} Table")