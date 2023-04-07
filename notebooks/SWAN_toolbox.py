# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 12:04:03 2019
Updated: 26-03-2021

@author: Leo Peach

A script for writing a SWAN run and input file

"""

import os
import datetime as dt

##for plottting
import matplotlib.pyplot as plt

##for reading the mesh
import read_mesh
from scipy.io import loadmat
import numpy as np
import pandas as pd

class SWAN_config_params():
    """
    A class object for the generation of SWAN run files
    """

    def __init__(self, run, end, meshname = 'GC_NOAAWW3_03', timestep = 30, timestepunit = 'MIN',
                  dirTheta = 5, flim = (0.038, 0.5), outtime = 1, outunit = "HR"):

        path = './'+run
        self.run = run

        self.end = end
        #check and see if the path exists
        if os.path.isdir(path) == True:
            path = path
        else:
            print("run files don't exist!")
        #path variables
        self.path = path
        self.inputPath = path+'/inputs'
        self.outputDir = path+'/outputs'
        self.meshPath = self.inputPath+'/MeshFiles'
        self.outputPoints = self.inputPath+'/PointFiles'
        self.results = path+'/results'


        self.meshname = meshname
        self.timestep = timestep
        self.timestepunit = timestepunit

        self.outtime = outtime
        self.outunit = "HR"

        self.flim = flim
        self.dirTheta = dirTheta
        self.dirBins = 360/dirTheta



    def header(self):
        """
        Generates a SWAN model run file Header

        Returns
        -------
        Header : String
            Returns a string of the model header.

        """

        Header = "$****************************************************************************\n$ Header\n$**************************************************************************** \n"
        Header2 = "PROJect "+"'Tweedv0.1' "+"'01' \n"
        Header3 = "\t 'Description: Operational Wave Model Tweed and Gold Coast' \n"
        Header4 = "\t \t 'Mesh: '\n"
        Header5 = "\t \t \t 'Start: "+self.run+" End: "+dt.datetime.strptime(self.end, "%Y%m%d%H%M").strftime("%Y%m%d_%H%M")+ " timesteps: "+str(self.timestep)+self.timestepunit+"'"
        Header = Header + Header2+ Header3 +Header4+Header5

        return Header

    def setup(self):
        setup = "$***************************************\n$ Model Setup\n$***************************************\n"
        setup2 = "SET 0. 90. 0.05 NAUTical \n"
        setup3 = "MODE NONSTATionary TWODimensional \n"
        setup4 = "COORDinates SPHERical \n"
        setup = setup+setup2+setup3+setup4

        return setup

    def comp_mesh(self):
        compMesh = "$***************************************\n$ Comp Mesh\n$***************************************\n"
        compMesh2 = "CGRID UNSTRUCtured CIRcle "+str(int(self.dirBins))+" "+str(self.flim[0])+" "+str(self.flim[-1])+"\n"
        compMesh3 = "READgrid UNSTRUCtured ADCirc $ as a fort.14 file in local directory\n"
        compMesh = compMesh+compMesh2+compMesh3
        return compMesh

    def bath_mesh(self):
        bathyMesh = "$***************************************\n $Bath Mesh\n$***************************************\n"
        bathyMesh2 = "$INPgrid BOTtom UNSTRUCtured \n"
        bathyMesh3 = "$READinp BOTtom -1. '"+self.meshPath+"/"+self.meshname+".bot' 1 0 FREE\n"
        bathyMesh = bathyMesh+bathyMesh2+bathyMesh3
        return bathyMesh

    def model_forcing_param(self):
        modforce = "$***************************************\n$Model Forcing\n$***************************************\n"
        modforce2 = "BOUnd SHAPespec JONswap PEAK DSPR DEGRees  $ only relevant is parameteric (TPAR) data is used'\n"
        modforce3 = "$ Eastern boundary (SIDE 1) ([len] is measured in deg CCW from SE corner) \n"
        modforce4 = "BOUndspec SIDE 1 VARiable FILE & \n"
        boundarys = [f for f in os.listdir(self.inputPath) if '.bnd' in f]
        boundarys.reverse()
        along = 0.00
        modforce5 = ""
        for file in boundarys:
            modforce5 += str("{:.2f}".format(along))+" '"+self.inputPath+"/"+file+"' 1 & \n"
            along += 1.97


        modforce = modforce+modforce2+modforce3+modforce4+modforce5

        return modforce

    def model_forcing(self):
        modforce = "$***************************************\n$Model Forcing\n$***************************************\n"
        #modforce2 = "BOUnd SHAPespec JONswap PEAK DSPR DEGRees  $ only relevant is parameteric (TPAR) data is used'\n"
        modforce3 = "$ Eastern boundary (SIDE 1) ([len] is measured in deg CCW from SE corner) \n"
        modforce4 = "BOUndspec SIDE 1 VARiable FILE & \n"
        boundarys = [f for f in os.listdir(self.inputPath) if '.sp2' in f]
        boundarys.reverse()
        along = 0.00
        modforce5 = ""
        for file in boundarys:
            modforce5 += str("{:.2f}".format(along))+" '"+self.inputPath+"/"+file+"' 1 & \n"
            along += 0.1

        ##adding two other boundaries
        #modforce6 = "$ Northern and southern boundary (SIDE 6 & 7) ([len] is measured in deg CCW from SE corner) \n"
        #modforce7 = "BOUndspec SIDE 6 VARiable FILE & \n"
        #modforce8 = "0.00 "+"'"+self.inputPath+"/"+boundarys[-1]+"' 1 \n"
        #modforce9 = "BOUndspec SIDE 7 VARiable FILE & \n"
        #modforce10 = "0.00 "+"'"+self.inputPath+"/"+boundarys[-1]+"' 1 \n"

        modforce = modforce+modforce3+modforce4+modforce5
        return modforce
    
    def wind_force(self):
        windforce = "$***************************************\n $Wind Forcing\n$***************************************\n"
        windforce2= "$ Regular input grid corresponding to the grid of the adopted wind model \n"
        windFile = [f for f in os.listdir(self.inputPath) if '.wnd' in f]
        with open(self.inputPath+"/"+windFile[0], 'r') as fp:
            for line in fp:
                if 'INPgrid' in line:
                    windforce3 = line
                if 'READinp' in line:
                    windforce4 = line
        fp.close()
        windforce = windforce+windforce2+windforce3+windforce4

        return windforce

    def water_level(self):
        waterlvl = "$***************************************\n $Water Level Variation\n$***************************************\n"
        waterlvl2 = "$ Regular input grid corresponding to 4 corners spanning the domain \n"
        waterFile = [f for f in os.listdir(self.inputPath) if '.wlv' in f]
        with open(self.inputPath+"/"+waterFile[0], 'r') as fp:
            for line in fp:
                if 'INPgrid' in line:
                    waterlvl3 = line
                if 'READinp' in line:
                    waterlvl4 = line
        fp.close()
        waterlvl = waterlvl+waterlvl2+waterlvl3+waterlvl4
        return waterlvl

    def model_physics(self):
        modelphy = "$***************************************\n $Model Physics\n$***************************************\n"
        modelphy2 = "$ Model formulation and wave growth \n"
        modelphy3 = "GEN3 WESTHuysen  \n \n"
        modelphy4 = "$ Shallow water wave-wave interation \n"
        modelphy5 = "TRIad 				\n"
        modelphy6 = "$ Bottom friction \n"
        modelphy7 = "FRICtion COLLins  \n"
        modelphy8 = "\n \n$ Depth induced breaking \n"
        modelphy9 = "$ BREaking CONstant \n"
        modelphy10 ="BREaking BKD  \n"

        modelphy = modelphy+modelphy2+modelphy3+modelphy4+modelphy5+modelphy6+modelphy7+modelphy8+modelphy9+modelphy10
        return modelphy

    def model_numerics(self):
        modelnum = "\n$***************************************\n $Model Numerics\n$***************************************\n"
        modelnum += "NUMeric STOPC 0.001 0.005 0.001 99.9 STAT 150 $  % defaults 0.005 0.01 0.005 99.5 detailed 0.001 0.005 0.001 99.9\n"
        modelnum += "$ Ensure outputs match WB frequencies \n"
        modelnum += "QUANTITY HS TM02 FSPR fmin=0.025 fmax=0.5 \n"   

        return modelnum

    
    def model_outputs(self):
        modelout = "$***************************************\n $Model Outputs\n$***************************************\n \n"
        modelout2 = "$ Point Output Locations \n"
        modelout3 = "POINTS 'OutPts' FILE '"+self.outputPoints+"/gc_OutPts.txt' & \n \n"
        modelout3a = "POINTS '10mPts' FILE '"+self.outputPoints+"/outputs_10m.txt' & \n \n"
        modelout3 = modelout3+modelout3a
        modelout4 = "$ Point Output - Integrated parameters \n"
        modelout5 = "TABLE 'OutPts' HEAD '"+self.results+"/gc_OutPtsIP.tbl' & \n"
        modelout6 = "TIME HSign HSWELL TPS TM02 DIR PDIR WATLev OUTput "+dt.datetime.strptime(self.run, "%Y%m%d_%H%M").strftime("%Y%m%d.%H%M%S")+" "+str(self.outtime)+" "+self.outunit+"\n"
        modelout5c = "SPECout 'OutPts' SPEC2D ABSolute '"+self.results+"/spec_WB.sp2' & \n"
        modelout6c = "OUTPUT "+dt.datetime.strptime(self.run, "%Y%m%d_%H%M").strftime("%Y%m%d.%H%M%S")+" "+str(self.outtime)+" "+self.outunit+"\n"
        modelout5a = "TABLE '10mPts' HEAD '"+self.results+"/Out10mPts.tbl' & \n"
        modelout6a = "TIME HSign HSWELL TPS TM02 DIR PDIR WATLev OUTput "+dt.datetime.strptime(self.run, "%Y%m%d_%H%M").strftime("%Y%m%d.%H%M%S")+" "+str(self.outtime)+" "+self.outunit+"\n"
        modelout5b = "SPECout '10mPts' SPEC2D ABSolute '"+self.results+"/spec10m.sp2' & \n"
        modelout6b = "OUTPUT "+dt.datetime.strptime(self.run, "%Y%m%d_%H%M").strftime("%Y%m%d.%H%M%S")+" "+str(self.outtime)+" "+self.outunit+"\n"
        modelout7 = "\n$ Wave parameters on grid \n"
        modelout8 = "BLOCK 'COMPGRID' NOHEAD '"+self.results+"/"+self.run+"_grid_WavePar.mat' & \n"
        modelout9 = "HSign TPS TM02 DIR PDIR WATLev  OUTput "+dt.datetime.strptime(self.run, "%Y%m%d_%H%M").strftime("%Y%m%d.%H%M%S")+" "+str(self.outtime)+" "+self.outunit+"\n"
        modelout = modelout+modelout2+modelout3+modelout4+modelout5+modelout6+modelout5c+modelout6c+modelout5a+modelout6a+modelout5b+modelout6b+modelout7+modelout8+modelout9
        return modelout

    def model_execute(self):
        modelrun = "$***************************************\n $Excecute Model\n$***************************************\n"
        modelrun1 = "$ Run the model \n"
        #step model back 12 hours for warm up
        start = dt.datetime.strptime(self.run, "%Y%m%d_%H%M") - dt.timedelta(hours = 12)

        modelrunA = "COMPute STationary "+ start.strftime("%Y%m%d.%H%M%S")+" \n"
        modelrun2 = "COMPute NONSTationary "+(start + dt.timedelta(minutes = 30)).strftime("%Y%m%d.%H%M%S")+" "+str(self.timestep)+" "+self.timestepunit+" "+(start + dt.timedelta(hours = 48)).strftime("%Y%m%d.%H%M%S")
        modelrun3 = "\n\n$Model End \n$******************************************************************\n"
        modelrun4 = "STOP"
        modelrun = modelrun+modelrun1+modelrunA+modelrun2+modelrun3+modelrun4
        return modelrun

    def build_file(self):
        """
        Builds the SWAN model run file as per the specifications provided.

        Returns
        -------
        String
            Returns a string of the .swn file generated.

        """
        with open(self.path+"/swan_mod_"+self.run+".swn", 'w') as f:
            f.write(self.header())
            f.write("\n")
            f.write(self.setup())
            f.write("\n")
            f.write(self.comp_mesh())
            f.write("\n")
            #f.write(self.bath_mesh()) No longer needed due to fort.14 mesh file
            f.write("\n")
            f.write(self.model_forcing())
            f.write("\n")
            f.write(self.wind_force())
            f.write("\n")
            f.write(self.water_level())
            f.write("\n")
            f.write(self.model_physics())
            f.write("\n")
            f.write(self.model_numerics())
            f.write("\n")
            f.write(self.model_outputs())
            f.write("\n")
            f.write(self.model_execute())
        f.close()
        return self.path+"/swan_mod_"+self.run+".swn"


# some useful methods
import wavespectra
import pandas as pd
import xarray as xr
import numpy as np


def waveParams(dap, station = False):
    """
    Creates wave params dataframe
    """
    
    ds = xr.open_dataset(dap)
    spec = wavespectra.read_dataset(ds)


    if station != False:
        spec = spec.sel(site = station)
        
    stats = spec.spec.stats(["hs", "tp", "dpm", "dspr"]).to_dataframe()
    #stats['dpm'] = 180 -stats.dpm
        
    if station == False:
        stats['site'] = stats.index.get_level_values('site')
        stats.index = stats.index.droplevel('site')
    
    spec.close()
    return stats

def waveParams_SWAN(my_swan, period = 'PEAK'):
    """
    Creates wave params dataframe, from a SWAN spectrum file
    """

    spec = wavespectra.read_swan(my_swan)
    
    stats = spec.spec.stats(["hs", "tm01", "tp", "dpm", "dspr"]).to_dataframe()



    stats.index = stats.index.droplevel('lat')
    stats.index = stats.index.droplevel('lon')
    #stats['dpm'] = 180 -stats.dpm
    if period == "PEAK":
        stats = stats[["hs", "tp", "dpm", "dspr"]]
    else:
        stats = stats[["hs", "tm01", "dpm", "dspr"]]

    return stats

def createTPAR(df, fname = 'test'):
    """Converts WaveParams dataframe to TPAR file
    """
    
    df = df.astype(float).round(2)
    df['time'] = df.index.strftime("%Y%m%d.%H%M%S")
    df['time'] = df['time'].astype(float)
    
    #SWAN uses a one sided direction spread
    df['dspr'] = round(df['dspr']/2, 3)
    
    
    
    np.savetxt(fname+".bnd", df[['time', 'hs','tp','dpm','dspr']].values, fmt='%1.6f %1.2f %1.2f %1.2f %1.1f', header= 'TPAR',comments='')
    return


############# Useful Plotting Functions ###########################

#### Plotting Methods ############

def plotSite_Hs(obs,model, name = "SiteName"):
    
    merged = pd.merge(obs,model, left_index = True, right_index = True)
    
    #plot Hs
    f, (a0, a1) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [3, 1]}, figsize = (20,5))
    #plot 1
    a0.set_ylim(0, merged.Hsig_x.max() + 0.5)
    a0.plot(merged.index, merged.Hsig_x, label = 'Obs')
    a0.plot(merged.index, merged.Hsig_y, label = 'Model')
    a0.set_ylabel('Hs (m)')
    a0.margins(x=0.01)
    a0.legend()
    #plot 2
    a1.set_aspect('equal')
    a1.set_xlim(merged.Hsig_x.min() -0.5, merged.Hsig_x.max() + 0.5)
    a1.set_ylim(merged.Hsig_x.min() -0.5, merged.Hsig_x.max() + 0.5)
    a1.plot([20,-1], [20,-1], color = 'grey')
    a1.plot(merged.Hsig_x, merged.Hsig_y, 'x')
    
    f.suptitle(name)
    
    plt.tight_layout()
   

    return f

def plotSite_Tz(obs,model, name = "SiteName"):
    
    merged = pd.merge(obs,model, left_index = True, right_index = True)
    
    #plot Tz
    f, (a0, a1) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [3, 1]}, figsize = (20,5))
    #plot 1
    a0.set_ylim(0, merged.Tm02.max() + 2.0)
    a0.plot(merged.index, merged.Tz, label = 'Obs')
    a0.plot(merged.index, merged.Tm02, label = 'Model')
    a0.set_ylabel('Tz (s)')
    a0.margins(x=0.01)
    a0.legend()
    #plot 2
    a1.set_aspect('equal')
    a1.set_xlim(merged.Tz.min() -0.5, merged.Tz.max() + 2.0)
    a1.set_ylim(merged.Tz.min() -0.5, merged.Tz.max() + 2.0)
    a1.plot([20,-1], [20,-1], color = 'grey')
    a1.plot(merged.Tz, merged.Tm02, 'x')
    
    f.suptitle(name)
    
    plt.tight_layout()
   

    return f

def plotSite_Tp(obs,model, name = "SiteName"):
    
    merged = pd.merge(obs,model, left_index = True, right_index = True)
    
    #plot Tp
    f, (a0, a1) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [3, 1]}, figsize = (20,5))
    #plot 1
    a0.set_ylim(0, merged.Tp.max() + 5.0)
    a0.plot(merged.index, merged.Tp, label = 'Obs')
    a0.plot(merged.index, merged.Tp_smoothed, label = 'Model')
    a0.set_ylabel('Tp (s)')
    a0.margins(x=0.01)
    a0.legend()
    #plot 2
    a1.set_aspect('equal')
    a1.set_xlim(merged.Tp.min() -0.5, merged.Tp.max() + 2.0)
    a1.set_ylim(merged.Tp.min() -0.5, merged.Tp.max() + 2.0)
    a1.plot([40,-1], [40,-1], color = 'grey')
    a1.plot(merged.Tp, merged.Tp_smoothed, 'x')
    
    f.suptitle(name)
    
    plt.tight_layout()
   

    return f


def plotSite_PkDir(obs,model, name = "SiteName"):
    """
    """
    
    merged = pd.merge(obs,model, left_index = True, right_index = True)
    
    #plot PkDir
    f, (a0, a1) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [3, 1]}, figsize = (20,5))
    #plot 1
    #a0.set_ylim(0, merged.Tz.max() + 2.0)
    a0.plot(merged.index, merged.Direction, label = 'Obs')
    a0.plot(merged.index, merged.PkDir, label = 'Model')
    a0.set_ylabel('Degrees ')
    a0.margins(x=0.01)
    a0.legend()
    #plot 2
    a1.set_aspect('equal')
    #a1.set_xlim(merged.Tz.min() -0.5, merged.Tz.max() + 2.0)
    #a1.set_ylim(merged.Tz.min() -0.5, merged.Tz.max() + 2.0)
    a1.plot([20,-1], [20,-1], color = 'grey')
    a1.plot(merged.Direction, merged.PkDir, 'x')
    
    f.suptitle(name)
    
    plt.tight_layout()
   

    return f

def plotContourMapAnimation(mesh, matList, timesteps = 12, param = 'Hsig'):
    """
    """
    mesh = read_mesh.Mesh(mesh)

    def read_mat(data, param):
        """read the item from the matlab file
        """
        keys = [key for key,val in data.items() if param in key]
        vals = [val[0] for key,val in data.items() if param in key]
        #convert to dataframe for speed
        data = pd.DataFrame(vals).T
        data.columns = keys
        #each column are the outputs at each node
        return data

    dataList = []
    for i in matList:
        dataList.append(read_mat(loadmat(i), param).iloc[:,:timesteps])
    

    data = pd.concat(dataList, axis = 1)

    from matplotlib import cm
    import matplotlib.animation as animation

    fig, ax = plt.subplots(figsize = (10,8))
    levels = np.linspace(0, int(data.max(axis = 1).max()), 100)
    im = ax.tricontourf(mesh.x, mesh.y, mesh.elements, mesh.z, levels =levels,cmap=plt.cm.viridis)
    ax.set_ylim((-28.4,-28.0))
    def animate(i):
        ax.cla()
        plt.cla()
        z = data.iloc[:,i]
        z = np.nan_to_num(z.values)
        im = ax.tricontourf(mesh.x, mesh.y, mesh.elements, z, levels =levels,cmap=plt.cm.viridis)
        title = ax.text(0.5,0.85, data.iloc[:,i].name, bbox={'facecolor':'w', 'alpha':0.5, 'pad':5},
                    transform=ax.transAxes, ha="center")
        ax.set_ylim((-28.4,-28.0))

    cbar = plt.colorbar(im)
    cbar.set_ticks(levels[::4])
    cbar.set_label('Hsig (m)')
    ani = animation.FuncAnimation(fig,animate, frames = range(len(data.columns)),interval=200,repeat=False, blit=False)
    

    return ani
