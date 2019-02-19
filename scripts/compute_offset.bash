#!/bin/bash

## Load Python 2.7.13
#module use /usrx/local/dev/modulefiles
#module load python/2.7.13


export pyPath="/usrx/local/dev/python/2.7.13/bin"
export platform=""

export myModules=${platform}"/gpfs/hps3/nos/noscrub/Sergey.Vinogradov/IT-hsofs.v2.0.2/lib/csdlpy-1.5.1"
export pythonCode=${platform}"/gpfs/hps3/nos/noscrub/Sergey.Vinogradov/IT-hsofs.v2.0.2/ush/offset-1.5.1/offset/compute.py"
export logFile=${platform}"/gpfs/hps3/nos/noscrub/polar/offset/offset.log"

#export dataTankPath="web"
#export dataTankPath=${platform}"/gpfs/gp1/dcomdev/us007003/"
export dataTankPath=${platform}"/gpfs/hps3/nos/noscrub/Sergey.Vinogradov/us007003/"
#export endDate="20190217"
export endDate="latest"

export outputFile=${platform}"/gpfs/hps3/nos/noscrub/Sergey.Vinogradov/IT-hsofs.v2.0.2/latest_coops.csv"
export tmpDir=${platform}"/gpfs/hps3/nos/noscrub/Sergey.Vinogradov/tmp/"

#export ftpLogin="svinogradov@emcrzdm"
#export ftpPath="/home/ftp/polar/estofs/offset/"

cd ${tmpDir}
PYTHONPATH=${myModules} ${pyPath}/python -W ignore ${pythonCode} -z ${endDate} -o ${outputFile} -t ${tmpDir} -p ${dataTankPath} # -u ${ftpLogin} -f ${ftpPath} #> ${logFile}
