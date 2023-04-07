# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 15:17:12 2019

@author: Leo Peach

Calibration stats module for calibration of SWAN models compared with observations
"""
import numpy as np
from scipy import stats

def bias(s, o):
    """
    

    Parameters
    ----------
    s : Ndarray
        Simulation array
    o : Ndarray
        observation array

    Returns
    -------
    float
        bias of the simulation and observation

    """

    r = s-o
    bias = r.mean()
    return round(bias, 2)

def RMSE(s, o):
    """
    

    Parameters
    ----------
    s : Ndarray
        Simulation array
    o : Ndarray
        observation array

    Returns
    -------
    float
        root mean squared error

    """

    rmserr = ((s - o) ** 2).mean() ** .5
    return round(rmserr, 2)

def dirRMSE(s, o):
    """

    Parameters
    ----------
    s : Ndarray
        Simulation array
    o : Ndarray
        observation array

    Returns
    -------
    float
        root mean squared error

    """
    

    return round((np.mean(np.absolute((180 - s) -  (180 - o))**2))** .5, 2)

def SI(s, o):
    """
    Scatter Index (RMSE applied as a percentage of the simulation)

    Parameters
    ----------
    s : Ndarray
        Simulation array
    o : Ndarray
        observation array

    Returns
    -------
    string
        the scatter index percentage as a string

    """

    SI = 100 * (np.std(o - s)/ np.mean(o))

    return round(SI, 1)


def cor_coef(s, o):
    """
    Return Pearson product-moment correlation coefficients.

    Parameters
    ----------
    s : Ndarray
        Simulation array
    o : Ndarray
        observation array

    Returns
    -------
    float
        correlation coefficient (r value)

    """


    correlation_coeficient = np.corrcoef(s, o)[0][-1]
    return round(correlation_coeficient,2)

def dir_ad(s, o):
    """
    The mean absolute differrence of directional data"""
    
    return round(np.mean(np.absolute((180 - s) -  (180 - o))), 2)


def NS(s, o):
    """
    Nash-Sutcliffe (1970)
    Answers the question: How well does the forecast predict the observed time series?

    Range: -∞ to 1. Perfect score: 1.

    Characteristics: Frequently used to quantify the accuracy of hydrological predictions. If E=0 then the model forecast is no more accurate than the mean of the observations; if E<0 then the mean observed value is a more accurate predictor than the model. The expression is identical to that for the coefficient of determination R2 and the reduction of variance.

    Parameters
    ----------
    s : Ndarray
        Simulation array
    o : Ndarray
        observation array

    Returns
    -------
    float
        nash sutcliffe index of efficiency

    """


    NS= 1 - sum((s-o)**2)/sum((o-np.mean(o))**2)
    return round(NS, 2)


def IofA(s, o):
    """
    Willimot et al (1980)
    Index of agreement

    Answers the question: How well does the forecast predict the observed time series?

    Range: 0 to 1. Perfect score: 1.
    
    Parameters
    ----------
    s : Ndarray
        Simulation array
    o : Ndarray
        observation array

    Returns
    -------
    float
        index of agreement

    """


    ia = 1 -(np.sum((o-s)**2))/(np.sum((np.abs(s-np.mean(o))+np.abs(o-np.mean(o)))**2))
    return round(ia, 2)

def r2(s,o):
    """
    Coeficient of determination
    Estimated through Linear Regression
    
    Range: 0 to 1. Perfect score: 1.

    Parameters
    ----------
    s : Ndarray
        Simulation array
    o : Ndarray
        observation array
        
    Returns
    -------
    float
        coeficient of determination

    """


    slope, intercept, r_value, p_value, std_err = stats.linregress(s, o)
    return round(r_value**2, 2)


def direction_to_euc(arr):
    """
    

    Parameters
    ----------
    arr : Ndarray
        Simulation array
    Returns
    -------
    Ndarray
        tuple containing euclidean distant components


    """

    arr_cos = np.sin(np.deg2rad(arr))
    arr_sin = np.cos(np.deg2rad(arr))

    return (arr_cos, arr_sin)


def all_stats(s, o):
    """
    

    Parameters
    ----------
    s : Ndarray
        Simulation array
    o : Ndarray
        observation array
        
    Returns
    -------
    mystats : dictionary
        the full suite of calibration stats

    """

    mystats = {}
    mystats['Bias'] = bias(s,o)
    mystats['Root Mean Squared Error'] = RMSE(s, o)
    mystats['Scatter Index'] = SI(s, o)
    mystats['Coefficient of Determination'] = r2(s,o)
    mystats['Coefficient of Efficiency'] = NS(s, o)
    mystats['Correlation Coefficient'] = cor_coef(s, o)
    mystats['Index of Agreement'] = IofA(s, o)
    return mystats

def dir_all_stats(s, o):
    """
    

    Parameters
    ----------
    s : Ndarray
        Simulation array
    o : Ndarray
        observation array
        
    Returns
    -------
    mystats : dictionary
        the full suite of calibration stats

    """

    mystats = {}
    mystats['Root Mean Squared Error'] = dirRMSE(s, o)
    mystats['Absolute Difference'] = dir_ad(s, o)
    mystats['Coefficient of Determination'] = r2(s,o)
    mystats['Coefficient of Efficiency'] = NS(s, o)
    mystats['Correlation Coefficient'] = cor_coef(s, o)
    mystats['Index of Agreement'] = IofA(s, o)
    return mystats
