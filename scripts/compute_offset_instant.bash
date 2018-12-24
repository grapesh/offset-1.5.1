#!/bin/bash

## Load Python 2.7.13
#module use /usrx/local/dev/modulefiles
#module load python/2.7.13

export pyPath="/usrx/local/dev/python/2.7.13/bin"
export platform=""

export myModules=${platform}"/gpfs/hps3/nos/noscrub/nwprod/csdlpy-1.5.1"
export pythonCode=${platform}"/gpfs/hps3/nos/noscrub/nwprod/offset-1.5.1/offset/compute.py"
export logFile=${platform}"/gpfs/hps3/nos/noscrub/polar/offset/offset.log"

export endDate="2018101012"
export outputFile=${platform}"/gpfs/hps3/nos/noscrub/polar/offset/coops_2018101012.csv"
export tmpDir=${platform}"/gpfs/hps3/nos/noscrub/tmp/offset/"

export ftpLogin="svinogradov@emcrzdm"
export ftpPath="/home/ftp/polar/estofs/offset/"

cd ${tmpDir}
PYTHONPATH=${myModules} ${pyPath}/python -W ignore ${pythonCode} -z ${endDate} -o ${outputFile} -t ${tmpDir} -u ${ftpLogin} -f ${ftpPath} # > ${logFile}
