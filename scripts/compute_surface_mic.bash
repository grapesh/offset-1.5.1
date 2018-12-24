#!/bin/bash

## Load Python 2.7.13
#module use /usrx/local/dev/modulefiles
#module load python/2.7.13

export pyPath="/usrx/local/dev/python/2.7.13/bin"
export platform=""

export myModules=${platform}"/gpfs/hps3/nos/noscrub/nwprod/csdlpy-1.5.1"
export pythonCode=${platform}"/gpfs/hps3/nos/noscrub/nwprod/offset-1.5.1/offset/interpolate.py"

export logFile=${platform}"/gpfs/hps3/nos/noscrub/polar/offset/interp.mic.log"

export NDAYS=${1:-2} # 2 days averaging by default. Change it to 1 to 7 if need be. 
export inputFile=${platform}"/gpfs/hps3/nos/noscrub/polar/offset/latest_coops.csv"
export gridFile="ftp://ocsftp.ncd.noaa.gov/estofs/mic/fort.14"
export outputFile=${platform}"/gpfs/hps3/nos/noscrub/polar/offset/mic/estofs.mic.offset.63"
export tmpDir=${platform}"/gpfs/hps3/nos/noscrub/tmp/offset/mic"

export ftpLogin="svinogradov@emcrzdm"
export ftpPath="/home/ftp/polar/estofs/offset/"

cd ${tmpDir}
PYTHONPATH=${myModules} ${pyPath}/python -W ignore ${pythonCode} -d ${NDAYS} -i ${inputFile} -o ${outputFile} -g ${gridFile} -t ${tmpDir} -u ${ftpLogin} -f ${ftpPath} > ${logFile}

