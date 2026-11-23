import glob 
import sys 
import pandas as pd 
from bokeh.io import save 
from bokeh.models import ColumnarDataSource, DataTable, TableColumn, NumberFormatter
from bokeh.resources import INLINE

data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
out_file = sys.argv[1] if len(sys.argv) > 1 else "data_table.html"

files = sorted(glob.glob(f"{data_dir}/*parquet"))
if not files: 
        raise SystemExit(f"no parquet files found in: '{data_dir}'!!")

df = pd.concat((pd.read_parquet(f) for f in files), ignore_index=True)
df.sort_values("window_start").reset_index(drop=True)

df["window_start"] = df["window_start"].dt.strftime("%Y-%m-%dT%H:%M:%S")

