import polars as pl
import re

class FeatureEngineering_Extend:

    def __init__(self, filename):
        self.filename = filename
        self.df = self.read_file(self.filename)
        self.df = self.parse_time_column(self.df, "Time of occurrence")  # parse datetime first
        self.output = self.run_output()

    def read_file(self, filename):
        # Reads CSV assuming UTF-8 encoding
        return pl.read_csv(filename, encoding="utf8")

    def run_output(self):
        df = self.add_times(self.df)
        df = self.extend_df(df)
        return df

    def parse_time_column(self, df, col_name):
        # Clean string, replace '-', and parse datetime
        df = df.with_columns(
            pl.col(col_name)
            .str.strip_chars('"')
            .str.replace("-", " ")
            .str.strptime(pl.Datetime, "%Y/%m/%d %H:%M", strict=False)
            .alias("Time")  # new datetime column
        )
        return df

    def add_times(self, df):
        # Extract year, month, week, day from Time
        time_fields = ["year", "month", "week", "day"]
        df = df.with_columns(
            [getattr(pl.col("Time").dt, time_field)().alias(time_field) for time_field in time_fields]
        )
        return df

    def extend_df(self, df):
        # Coordinates Taipei Main Station
        tpe_main_stationX = 121.5170
        tpe_main_stationY = 25.0475

        # Extract address components
        structures = self.address_pattern()
        extract_exprs = [
            df['Location of accident'].str.extract(pattern, 0).alias(name)
            for name, pattern in structures
        ]

        # Compute Euclidean distance from Taipei Main Station
        distance_expr = (
            ((pl.lit(tpe_main_stationX) - pl.col("CoordinateX"))**2 +
             (pl.lit(tpe_main_stationY) - pl.col("CoordinateY"))**2).sqrt()
            .alias("distance_to_tpe_main_station")
        )

        # Apply all expressions in one call
        df = df.with_columns(extract_exprs + [distance_expr])

        # Convert all string columns to categorical
        df = df.with_columns([
            df[name].str.strip_chars().cast(pl.Categorical)
            for name in df.columns
            if df[name].dtype == pl.Utf8
        ])

        return df

    @staticmethod
    def address_pattern():
        return [
            ("district", r".+?區"),
            ("road", r".+?(路|街|大道|橋|圓環|廣場)"),
            ("section", r"\d+段"),
            ("lane", r"\d+巷"),
            ("alley", r"\d+弄|\d+衖"),
            ("number", r"\d+號"),
            ("floor", r"\d+樓"),
            ("room", r"\d+室"),
        ]
