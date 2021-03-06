#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: Sergey.Vinogradov@noaa.gov
"""
import csdlpy
import os, sys
import argparse
import numpy as np
import datetime
from datetime import timedelta as dt

#==============================================================================
def timestamp():
    print '------'
    print '[Time]: ' + str(datetime.datetime.utcnow()) + ' UTC'
    print '------'
        
#==============================================================================
def read_cmd_argv (argv):

    parser = argparse.ArgumentParser()
    
    parser.add_argument('-d','--nDays',          required=True)    
    parser.add_argument('-i','--inputFile',      required=True)
    parser.add_argument('-e','--excludeList',    required=True)
    parser.add_argument('-o','--outputFile',     required=True)
    parser.add_argument('-c','--pltCfgFile',     required=True)
    parser.add_argument('-t','--tmpDir',         required=True)
    parser.add_argument('-u','--ftpLogin',       required=True)
    parser.add_argument('-f','--ftpPath',        required=True)
    
    args = parser.parse_args()           
    print '[info]: offset/interpolate.py is configured with :', args
    return args
    
#==============================================================================
def interpolate_offset(argv):

    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))    
    from offset import plot
    
    #Receive command line arguments
    args = read_cmd_argv(argv)

    #Read config file 
    pp = csdlpy.plotter.read_config_ini (args.pltCfgFile)
    
    #Get the files
    gridFile      = os.path.join(args.tmpDir, 'fort.14')
    coastlineFile = os.path.join(args.tmpDir,'coastline.dat')
    
    csdlpy.transfer.download ( pp['Grid']['url'], gridFile )
    csdlpy.transfer.download ( pp['Coastline']['url'], coastlineFile)
    coast  = csdlpy.plotter.readCoastline(coastlineFile)    

    #Get the boundaries from the grid
    grid = csdlpy.adcirc.readGrid (gridFile)
    xlim = min(grid['lon']), max(grid['lon'])
    ylim = min(grid['lat']), max(grid['lat'])

    #Read bias table
    xo = []
    yo = []
    zo = []
    #print '[debug]: ndays=', args.nDays
    query = ['NOSID', 'NWSID', 'Lon', 'Lat', '7','6','5','4','3','2','1']
    if args.nDays == '0':
        query = ['NOSID', 'NWSID', 'Lon', 'Lat', '0']
    print '[info]: Reading WL anomalies from ', args.inputFile
    master = csdlpy.obs.parse.stationsList (args.inputFile,   query)

    print '[info]: Reading stations to be excluded from ', args.excludeList
    exclud = csdlpy.obs.parse.stationsList (args.excludeList, ['NOSID'])

    for m in master:
        badid = False
        nosid = float(m[query.index('NOSID')])
        for e in exclud:
            if nosid == float(e[query.index('NOSID')]):
                print '[warn]: station ',nosid,' is in exclude list.'
                badid = True
        xd = float(m[query.index('Lon')])
        yd = float(m[query.index('Lat')])
        zd = m[query.index(args.nDays)]
        if not badid and not zd=='nan' and xlim[0] <= xd and xd <= xlim[1] and ylim[0] <= yd and yd <= ylim[1]:
            xo.append(xd)
            yo.append(yd)
            zo.append(float(zd))
    print '[info]: data points selected within the grid coverage : ' + str(len(xo))
    
    timestamp()
    offsetNote = 'ADCIRC Offset. NDAYS=' + args.nDays + \
                     '. Created:' + str(datetime.datetime.utcnow())
    offsetField = np.zeros(len(grid['depth']), dtype=float)

    # Parse for dates
    with open(args.inputFile) as f:
        header = f.readline()
    datestr = header.split(',')[-2].split(':')[-1]
    if len(datestr)==8:
        endDate   = datetime.datetime.strptime(datestr, '%Y%m%d')
        startDate = endDate - dt(days=int(args.nDays))
        plotTitle = args.nDays + ' DAYS:' + \
                startDate.strftime('%Y%m%d') +'--'+ endDate.strftime('%Y%m%d')

    if len(datestr)>=10:
       endDate   = datetime.datetime.strptime(datestr, '%Y%m%d%H%M') + dt(minutes=12)
       startDate = datetime.datetime.strptime(datestr, '%Y%m%d%H%M') - dt(minutes=12) 
       plotTitle = args.nDays + ' DATE:' + \
                startDate.strftime('%Y%m%d %H:%M') +'--'+ endDate.strftime('%Y%m%d %H:%M')

    if len(xo)>0:
        #Prep interpolation
        Zfull  = 0.    # Depths where the solution is fully untapered 
        Znull  = 200.  # Depths where the solution is fully tapered 
        Pow    = 2.0   # Interpolation power
        Radius = 2.5   # Proximity radius, in degrees
    
        #Interpolate on the continental shelf
        iShelf = np.where ( grid['depth'] < Znull )[0]
    
        offsetField [iShelf] = csdlpy.interp.shepard_idw (xo, yo, zo, \
                                      grid['lon'][iShelf], \
                                      grid['lat'][iShelf],  Pow) 
    
        timestamp() 
        # Taper the result with depth
        iTaper = np.where ( np.logical_and (Zfull <= grid['depth'], \
                                            Znull >= grid['depth']) )[0]

        offsetField [iTaper] = csdlpy.interp.taper_linear (Zfull, Znull, \
                                                  grid['depth'][iTaper], \
                                                  offsetField  [iTaper])

        timestamp()
        #Taper off the results not in proximity of the obs
        dist  = csdlpy.interp.distance_matrix (xo, yo, grid['lon'], grid['lat'])
        iDist = np.where ( np.nanmin(dist, axis=1) > Radius ) 
        offsetField [iDist] = 0.0

    timestamp()
    #Write output    
    csdlpy.adcirc.writeOffset63 (offsetField, args.outputFile, offsetNote)

    timestamp()
    #Plot
    plotFile = os.path.join( args.tmpDir, \
               os.path.basename(args.outputFile)+'.' + args.nDays + 'days.png')

    plot.surface(offsetField, grid, coast, pp, plotTitle, plotFile)  

    #Upload 
    csdlpy.transfer.upload(plotFile, args.ftpLogin, args.ftpPath)
 
#==============================================================================    
if __name__ == "__main__":

    timestamp()
    interpolate_offset (sys.argv[1:])
    timestamp()

