from typing import Literal
import pandas as pd

class MergeUtils:
    @staticmethod
    def merge_dataframes(df1, df2, on, how: Literal['left', 'right', 'inner', 'outer', 'cross'] = 'left')-> pd.DataFrame:
        if on not in df1.columns or on not in df2.columns:
            raise ValueError(f"Column '{on}' not found in both dataframes")
        return pd.merge(df1, df2, on=on, how=how)

