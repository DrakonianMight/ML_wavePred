# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 22:01:31 2020

@author: leope
"""

import numpy as np
import pandas as pd



def convDirection(series):
    """necessary to convert direction for model training"""

    rads = np.deg2rad(series)
    
    return np.sin(rads), np.cos(rads)


def get_latest_obs():
    import requests

    path = "https://www.data.qld.gov.au/datastore/dump/2bbef99e-9974-49b9-a316-57402b00609c?format=json"
    #extract data from the opendata data portal
    s = requests.session()
    r = requests.get(path).json()

    fields = [f['id'] for f in r['fields']]
    data = pd.DataFrame(r['records'], columns = fields)
    s.close()

    #append to database
    data.index = pd.to_datetime(data.DateTime)
    data = data.drop('DateTime', 1)
    return data

def get_waveDB_xday_obs(dbpath = 'F:/SWAN/wave_obs.db', days = 7):
    import sqlite3
    wb_db = dbpath
    conn = sqlite3.connect(wb_db)
    wb_data = pd.read_sql_query("SELECT * FROM wave_obs WHERE DateTime > (SELECT DATETIME('now', '-"+str(days)+" day'))", conn)
    conn.close()
    
    wb_data.index = pd.to_datetime(wb_data.DateTime)
    wb_data = wb_data.sort_index()
    
    return wb_data

def getLocations(df):
    grpby = df.groupby('Site')
    MonLocations = []
    for name, site in grpby:
        MonLocations.append(site.sort_index().iloc[0][['Site','Latitude','Longitude']].values)
        
    locations = pd.DataFrame(MonLocations)
    locations.columns = ['name','lat','lon']
    return locations

def paramsDFList(df):
    """Refactors data for interactive plotting"""
    grpby = df.groupby('Site')
    Hsig = []
    Tz = []
    direction = []
    siteName=  []
    for name, site in grpby:
        Hsig.append(site.sort_index()[['Hsig']])
        Tz.append(site.sort_index()[['Tz']])
        direction.append(site.sort_index()[['Direction']])
        siteName.append(name)
    from functools import reduce
    HsigDF = reduce(lambda left, right: pd.merge(left, right, left_index = True, right_index = True), Hsig)
    TzDF = reduce(lambda left, right: pd.merge(left, right, left_index = True, right_index = True), Tz)
    directionDF = reduce(lambda left, right: pd.merge(left, right, left_index = True, right_index = True), direction)
    HsigDF.columns = siteName
    HsigDF.index.rename('datetime')
    TzDF.columns = siteName
    TzDF.index.rename('datetime')
    directionDF.columns = siteName
    directionDF.index.rename('datetime')
    return [HsigDF, TzDF,directionDF]

def processObs(df, siteList = ['Brisbane Mk4','Tweed Heads Mk4']):
    """
    Parameters
    ----------
    df : dataframe
        pandas dataframe of wave observations
    siteList : dataframe, optional
        DESCRIPTION. The default is ['Brisbane Mk4','Tweed Heads Mk4'].

    Returns
    -------
    data : dataframe
        dataframe of the data sorted and structured for ML model

    """
    
    dfList = []
    for site in siteList:
        sitedf = df[df['Site'] == site][['Hsig','Hmax','Tz','Tp','Direction']]
        colNames = []
        for col in sitedf.columns:
            colNames.append(col+('_'+site[:4]))
        sitedf.columns = colNames
        
        sitedf['dir_sin'+site[:4]], sitedf['dir_cos'+site[:4]] = convDirection(sitedf[colNames[0]])
        dfList.append(sitedf)
    from functools import reduce

    data = reduce(lambda left, right: pd.merge(left, right, left_index = True, right_index = True), dfList)
    data = data[data.columns.drop(list(data.filter(regex='Direction')))]
    return data