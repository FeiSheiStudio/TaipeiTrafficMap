# Data Processing
import pandas as pd

# Working according to OOP principles
from pydantic import BaseModel, DirectoryPath
from typing import List, AnyStr

# Working with directories
import os
from pathlib import Path




class Import_Data(BaseModel):
    # Retrieve the data from folder "data"

    project_folder: DirectoryPath = Path.cwd().resolve().parent
    data_folder: DirectoryPath = Path.cwd().resolve().parent / "data"
    csv_files: List[Path] = list( (Path.cwd().resolve().parent / "data").glob("*.csv"))

    ##
    output_path: AnyStr = os.path.join((Path.cwd().resolve().parent / 'data'), "combined.csv")

    def combine_csv_files(self) -> pd.DataFrame:
        header_dict = {"發生時間":"Time of occurrence",
    "處理別":"Type of treatment",
    "肇事地點": "Location of accident",
    "座標-X": "CoordinateX",
    "座標-Y": "CoordinateY" }


        dfs = []
        for ifile in self.csv_files:
            file = pd.read_csv(ifile, encoding= 'cp950')
            file.rename(columns = header_dict, inplace = True)
            dfs.append(file)

        combined_df = pd.concat(dfs, ignore_index = True)
        return combined_df

    def save_combined(self):
        combined_df = self.combine_csv_files()
        combined_df.to_csv(self.output_path)