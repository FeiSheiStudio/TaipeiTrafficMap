
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
        self.traffic_folder = self.data_folder / "Traffic Data"
        self.mrt_folder = self.data_folder / "MRT Data"

        self.traffic_files = list(self.traffic_folder.glob("*.csv"))
        self.output_path_traffic = self.data_folder / "combined.csv"


        self.mrt_csv = next(self.mrt_folder.glob("*.csv"))
        self.output_path_mrt = self.data_folder / 'mrt_fixed.csv'


    def read_mrt_file(self):
        # Assume 1 file only
        df = pl.read_csv(self.mrt_csv)

        df = (
            df
            .with_columns(
                pl.col("StationPosition")
                .str.replace_all(r"[{}']", "")
                .str.split(",")
            )
            .with_columns(
                [
                    pl.col("StationPosition").list.get(0).cast(pl.Float64).alias("lat"),
                    pl.col("StationPosition").list.get(1).cast(pl.Float64).alias("lon"),
                ]
            )
            .with_columns(
                pl.col("StationName")
                .str.replace_all(r"[^\u4e00-\u9fff]", "")  # Keep only Chinese characters
            )
            .drop("StationPosition")
        )

        df = self.filter_coordinates(df, 'lon', 'lat')

        return df

    def combine_traffic_files(self):
        header_dict = {
            "發生時間": "Time of occurrence",
            "處理別": "Type of treatment",
            "肇事地點": "Location of accident",
            "座標-X": "lon",
            "座標-Y": "lat"
        }
        dfs = []

        for ifile in self.traffic_files:
            if ifile != self.output_path_traffic:
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
            .str.strptime(pl.Datetime, "%Y/%m/%d %H:%M", strict=True)
            .alias("Time"),
            pl.col("Location of accident").str.strip_chars('"').alias(
                "Location of accident")
        ])
        combined = self.filter_coordinates(combined, "lon", "lat")
        return combined


    def fix_single_month_day(self, string):
     # 2019/1/2 08:37
     # Pad single-digit month/day
     fixed_string = re.sub(r'(\d{4})/(\d{1,2})/(\d{1,2})',
                     lambda m: f"{m.group(1)}/{int(m.group(2)):02d}/{int(m.group(3)):02d}",
                     string)
     # output: 2019/01/02 08:37
     return fixed_string

    def save_all(self):
        combined_traffic = self.combine_traffic_files()
        combined_traffic.write_csv(self.output_path_traffic)

        fixed_mrt = self.read_mrt_file()
        fixed_mrt.write_csv(self.output_path_mrt)
        return

    def filter_coordinates(self, dataset, coordx, coordy):
        dataset = dataset.filter(
            pl.col(coordx).is_finite() & pl.col(coordy).is_finite()
        )
        return dataset




