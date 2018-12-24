#!/bin/bash

## Load Python 2.7.13
#module use /usrx/local/dev/modulefiles
#module load python/2.7.13

export pyPath="/usrx/local/dev/python/2.7.13/bin"
export platform=""

export myModules=${platform}"/gpfs/hps3/nos/noscrub/nwprod/csdlpy-1.5.1"
export pythonCode=${platform}"/gpfs/hps3/nos/noscrub/nwprod/offset-1.5.1/offset/interpolate.py"

export logFile=${platform}"/gpfs/hps3/nos/noscrub/polar/offset/interp.atl.log"

export NDAYS=0 #${1:-2} # 2 days averaging by default. Change it to 1 to 7 if need be. 
export inputFile=${platform}"/gpfs/hps3/nos/noscrub/polar/offset/coops_2018101012.csv"
export pltCfgFile=${platform}"/gpfs/hps3/nos/noscrub/nwprod/offset-1.5.1/scripts/config.plot.offset.al142018.ini"
export outputFile=${platform}"/gpfs/hps3/nos/noscrub/polar/offset/atl/estofs.atl.offset.63.2018101012"
export tmpDir=${platform}"/gpfs/hps3/nos/noscrub/tmp/offset/atl"

export ftpLogin="svinogradov@emcrzdm"
export ftpPath="/home/www/polar/estofs/offset/"

cd ${tmpDir}
PYTHONPATH=${myModules} ${pyPath}/python -W ignore ${pythonCode} -d ${NDAYS} -i ${inputFile} -o ${outputFile} -c ${pltCfgFile} -t ${tmpDir} -u ${ftpLogin} -f ${ftpPath} # > ${logFile}

