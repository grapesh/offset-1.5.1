#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: Sergey.Vinogradov@noaa.gov
"""
import csdlpy
import numpy as np
import os, sys
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
import argparse

#==============================================================================
def read_cmd_argv (argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('-d','--nDays',          required=True)
    parser.add_argument('-i','--inputFile',      required=True)
    parser.add_argument('-c','--pltCfgFile',     required=True)
    parser.add_argument('-t','--tmpDir',         required=True)
    parser.add_argument('-u','--ftpLogin',       required=True)
    parser.add_argument('-f','--ftpPath',        required=True)

    args = parser.parse_args()
    print '[info]: offset/plot.py is configured with :', args
    return args

#=====================================================================
def surface(offset, grid, coast, pp, mapTitle, mapFile):

    # Default plotting limits, based on advisory track, first position
    lonlim = np.min(grid['lon']), np.max(grid['lon'])
    latlim = np.min(grid['lat']), np.max(grid['lat'])
    clim   = 0.,4.5
    try:
        lonlim = float(pp['Limits']['lonmin']),float(pp['Limits']['lonmax'])
        latlim = float(pp['Limits']['latmin']),float(pp['Limits']['latmax'])
        clim   = float(pp['Limits']['cmin']),  float(pp['Limits']['cmax'])
    except: #default limits, in case if not specified in ini file
        pass
    # Find maximal maxele value within the coord limits
    maxmax = np.max(offset)
    lonmax = grid['lon'][np.where(offset==maxmax)]
    latmax = grid['lat'][np.where(offset==maxmax)]
    print '[info]: max maxele = ',str(maxmax),'at ',str(lonmax),'x',str(latmax)

    f = csdlpy.plotter.plotMap(lonlim, latlim, fig_w=10., coast=coast)
    csdlpy.plotter.addSurface (grid, offset, clim=clim)

    maxStr = 'MAX VAL='+ str(np.round(maxmax,1)) + ' '
    try:
        maxStr = maxStr + pp['General']['units'] #+', '+ pp['General']['datum']
    except:
        pass # in case if there is a problem with pp
    plt.text (lonlim[0]+0.01, latlim[1]-2., maxStr, fontsize='7')

    plt.text (lonlim[0]+0.01, latlim[1]+0.1,'NOAA / OCEAN SERVICE')
    plt.plot(lonmax, latmax, 'ow',markerfacecolor='k',markersize=8)
    plt.plot(lonmax, latmax, 'ow',markerfacecolor='r',markersize=4)
    plt.text (lonmax+0.05,latmax+0.05, str(np.round(maxmax,1)),color='k',fontsize=6)
    
    #plt.title(datespan,fontsize=8)
    if mapTitle is not None:
        plt.title(mapTitle, fontsize=7) 
    plt.savefig(mapFile)
    plt.close()   

#=====================================================================
def biases(argv):

    #Receive command line arguments
    args = read_cmd_argv(argv)

    #Read config file 
    pp = csdlpy.plotter.read_config_ini (args.pltCfgFile)

    #Get the files
    coastlineFile = os.path.join(args.tmpDir,'coastline.dat')

    csdlpy.transfer.download ( pp['Coastline']['url'], coastlineFile)
    coast  = csdlpy.plotter.readCoastline(coastlineFile)
    xlim = (float(pp['Limits']['lonmin']), float(pp['Limits']['lonmax']))
    ylim = (float(pp['Limits']['latmin']), float(pp['Limits']['latmax']))

    #Read bias table
    xo = []
    yo = []
    zo = []
    query = ['NOSID', 'NWSID', 'Lon', 'Lat', '7','6','5','4','3','2','1']
    if args.nDays == '0':
        query = ['NOSID', 'NWSID', 'Lon', 'Lat', '0']
    print '[info]: Reading WL anomalies from ', args.inputFile
    master = csdlpy.obs.parse.stationsList (args.inputFile,   query)

    for m in master:
        xo.append( float(m[query.index('Lon')]) )
        yo.append( float(m[query.index('Lat')]) )
        zo.append( float(m[query.index(args.nDays)]) )
    print '[info]: data points selected within the grid coverage : ' + str(len(xo))

    with open(args.inputFile) as f:
        first_line = f.readline()
    valid = first_line.split(',')[-2].strip()
    print '[info]: valid ', valid
    csdlpy.plotter.plotMap (xo,yo,fig_w=16.0,lonlim=xlim,latlim=ylim, coast=coast)
    csdlpy.plotter.addTriangles((xo,yo,zo))

    string='MEAN WL ANOMALIES (IN METERS MSL) AVERAGED OVER ' + str(args.nDays) + ' UTC DAYS PRIOR TO ' + valid[-9:]
    plt.text(-120, -15, string)
    plotFile = os.path.join(args.tmpDir, 'map-biases-' + str(args.nDays).zfill(3) +'days.png')
    csdlpy.plotter.save    ('NOAA / NATIONAL OCEAN SERVICE ACTIVE STATIONS', plotFile )

    csdlpy.transfer.upload(plotFile, args.ftpLogin, args.ftpPath)

#=====================================================================
if __name__ == "__main__":
    biases (sys.argv[1:])
