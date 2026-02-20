# full_heatmap_pipeline.py
import polars as pl
import numpy as np
import re

# ----------------------------
# 1️⃣ Feature Engineering
# ----------------------------
class FeatureEngineering_Extend:

    def __init__(self, filename):
        self.filename = filename
        self.df = self.read_file()
        self.df = self.parse_time_column("Time of occurrence")  # parse datetime
        self.output = self.run_output()

    def read_file(self):
        # Reads CSV assuming UTF-8 encoding
        return pl.read_csv(self.filename, encoding="utf8")

    def parse_time_column(self, col_name):
        df = self.df.with_columns(
            pl.col(col_name)
            .str.strip_chars('"')
            .str.replace("-", " ")
            .str.strptime(pl.Datetime, "%Y/%m/%d %H:%M", strict=True)
            .alias("Time")
        )
        # Optional: clean Location string
        df = df.with_columns(
            pl.col('Location of accident').str.replace_all(r"\(", "")
        )
        self.df = df
        return df

    def run_output(self):
        df = self.add_times(self.df)
        df = self.extend_df(df)
        return df  # keep as Polars DataFrame

    def add_times(self, df):
        # Extract year, month, week, day from Time
        time_fields = ["year", "month", "week", "day"]
        df = df.with_columns(
            [getattr(pl.col("Time").dt, field)().alias(field) for field in time_fields]
        )
        # Add count column
        df = df.with_columns(pl.lit(1).alias('count'))
        return df

    def extend_df(self, df):
        # Taipei Main Station coordinates
        lat0, lon0 = 25.0475, 121.5170

        # Extract address components
        extract_exprs = [
            df['Location of accident'].str.extract(pattern, 0).alias(name)
            for name, pattern in self.address_pattern()
        ]

        # Compute Euclidean distance from Taipei Main Station
        distance_expr = (
            (
                ((pl.col("lat") - lat0) * 111) ** 2 +
                ((pl.col("lon") - lon0) * 111 * np.cos(np.radians(lat0))) ** 2
            ).sqrt().alias("distance_to_tpe_main_station")
        )

        df = df.with_columns(extract_exprs + [distance_expr])

        # Convert string columns to categorical
        df = df.with_columns([
            df[name].str.strip_chars().cast(pl.Categorical)
            for name in df.columns
            if df[name].dtype == pl.Utf8
        ])

        # Drop rows missing essential info
        df = df.drop_nulls(subset=['lat', 'lon', 'district'])
        return df

    @staticmethod
    def address_pattern():
        return [
            ("district", r".+?區"),
            ("road", r"[^與\(]+?(路|街|大道|橋|圓環|廣場)"),
            ("section", r"\d+段"),
            ("lane", r"\d+巷"),
            ("alley", r"\d+弄|\d+衖"),
            ("number", r"\d+號"),
            ("floor", r"\d+樓"),
            ("room", r"\d+室")
        ]