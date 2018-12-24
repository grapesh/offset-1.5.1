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
    
    parser.add_argument('-z','--endDate',        required=True)    
    parser.add_argument('-o','--outputFile',     required=True)
    parser.add_argument('-t','--tmpDir',         required=True)
    parser.add_argument('-u','--ftpLogin',       required=True)
    parser.add_argument('-f','--ftpPath',        required=True)
    
    args = parser.parse_args()           
    if 'latest' in args.endDate:
        args.endDate = datetime.datetime.utcnow().strftime("%Y%m%d")
 
    print '[info]: offset.compute.py is configured with :', args
    return args

    
#==============================================================================
def compute_offset(argv):

    MAXNDAYS = 7

    #sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))    
    #from offset import plot
    
    #Receive command line arguments
    args = read_cmd_argv(argv)

    #Retrieve active stations list
    active = csdlpy.obs.coops.getActiveStations()
    print '[info]: Number of active stations: ' +str(len(active['nos_id']))

    #Set up date span
    # If args.endDate is specified with hours, take quazi-instantaneous values
    isInstantaneous = False
    if len(args.endDate) == 10:
        dates = [datetime.datetime.strptime(args.endDate,"%Y%m%d%H")+dt(minutes=12), \
                 datetime.datetime.strptime(args.endDate,"%Y%m%d%H")-dt(minutes=12)]
        MAXNDAYS=0
        isInstantaneous = True
    else:    
        dates = [datetime.datetime.strptime(args.endDate,"%Y%m%d") \
                      - dt(days=x) for x in range(0,MAXNDAYS)]
 

    myDays   = range(MAXNDAYS,0,-1) # 7,6,5,4,3,2,1
    myBiases = np.zeros([len(active['nos_id']),MAXNDAYS], dtype=float)

    fid = open(args.outputFile, 'w')
    header = 'NOSID,NWSID,Lon,Lat,' + \
              ','.join(str(e) for e in myDays) + ', valid:' + args.endDate + ',\n'
    if isInstantaneous:
        header='NOSID,NWSID,Lon,Lat,0, valid:' + args.endDate + ',\n'
    fid.write( header )

    #Retrieve obs, compute biases
    for k in range(len(active['nos_id'])):

        nosid = str(active['nos_id'][k])
        nwsid = str(active['nws_id'][k])
        lon   = str(active['lon'][k])
        lat   = str(active['lat'][k])
 
        try:
            sline    = nosid + ',' + nwsid + ',' + lon + ',' + lat + ','
            print sline
            data     = csdlpy.obs.coops.getData(nosid, [dates[-1], dates[0]], \
                                                product='waterlevelrawsixmin')
            obsValues = data['values']
            obsDates  = data['dates']     

            # Compute offsets
            if isInstantaneous:
                sline = sline + str (np.nanmean(obsValues)) + ','
            else: 
                for n in range(len(dates)-1,-1,-1):
                    d0              = min( obsDates, key=lambda x: abs(x-dates[n]))
                    indx            = obsDates.index(d0) 
                    myBiases[k,n]   = np.nanmean(obsValues[indx:])
                    sline           = sline + str(myBiases[k,n]) + ','

            fid.write(sline + '\n')
        except:
            pass
    #Save 
    fid.close() 
    
    #Upload 
    csdlpy.transfer.upload(args.outputFile, args.ftpLogin, args.ftpPath)
    
    #Cleanup
    csdlpy.transfer.cleanup(args.tmpDir)
 
#==============================================================================    
if __name__ == "__main__":

    timestamp()
    compute_offset (sys.argv[1:])
    timestamp()

