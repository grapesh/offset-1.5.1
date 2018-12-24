#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: Sergey.Vinogradov@noaa.gov
"""
import csdlpy
import numpy as np
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt

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

