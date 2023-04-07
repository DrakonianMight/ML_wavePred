#########################################################
#
#   Read SWAN TPAR file
#   Created By: Leo Peach    
#   More info: 
#   Requirements: numpy, pandas, os
#
#########################################################

import pandas as pd

def readTPAR(path):
    """Read a SWAN TPAR file to a pandas dataframe"""

    df = pd.read_csv(path, skiprows = 1, header = None)
    df = df[0].astype(str).str.split(expand = True)

    df.index = pd.to_datetime(df[0].astype(str), format = "%Y%m%d.%H%M%S")
    df = df.loc[:, 1:]

    cols = df.columns
    df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')

    df.columns = ['Hs','Tp','pDir','Spr']

    return df