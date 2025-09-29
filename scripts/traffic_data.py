
# Working with directories
from pathlib import Path

# Do all data processing
import polars as pl
import pandas as pd

import re
from io import StringIO

class DataImport:
    def __init__(self):
        self.project_folder = Path.cwd().resolve().parent
        self.data_folder = self.project_folder / "data"
        self.csv_files = list(self.data_folder.glob("*.csv"))
        self.output_path = self.data_folder / "combined.csv"
        self.combined_df = self.combine_csv_files()

    def combine_csv_files(self):
        header_dict = {
            "發生時間": "Time of occurrence",
            "處理別": "Type of treatment",
            "肇事地點": "Location of accident",
            "座標-X": "CoordinateX",
            "座標-Y": "CoordinateY"
        }
        dfs = []

        for ifile in self.csv_files:
            if ifile != self.output_path:
                file = pd.read_csv(ifile,   encoding="cp950")
                df = pl.from_pandas(file)
                dfs.append(df)
        # Concatenate all CSVs and convert headers in english
        combined = pl.concat(dfs)
        combined = combined.rename(header_dict)

        combined = combined.with_columns([
            pl.col("Time of occurrence")
            .str.replace_many({'"': '', '-': ' '})
            .map_elements(self.fix_single_month_day, return_dtype = pl.Utf8)
            .str.strptime(pl.Datetime, "%Y/%m/%d %H:%M", strict=False)
            .alias("Time"),
            pl.col("Location of accident").str.strip_chars('"').alias(
                "Location of accident")
        ])
        return combined


    def fix_single_month_day(self, string):
     # 2019/1/2 08:37
     # Pad single-digit month/day
     fixed_string = re.sub(r'(\d{4})/(\d{1,2})/(\d{1,2})',
                     lambda m: f"{m.group(1)}/{int(m.group(2)):02d}/{int(m.group(3)):02d}",
                     string)
     # output: 2019/01/02 08:37
     return fixed_string

    def save_combined(self):
        combined_df = self.combine_csv_files()
        combined_df.write_csv(self.output_path)

