#! /bin/bash

set -o nounset
set -o errexit

tarfile=$1
mass=$2
filename="${tarfile%.*}"

echo 'creating directory'
mkdir -p impacts_$filename
cp $tarfile impacts_$filename/.
cd impacts_$filename
echo 'untarring files'
tar -xf $tarfile

echo 'initial fit'
combineTool.py -M Impacts -d */$mass/workspace.root -m $mass --doInitialFit --robustFit 1 -t -1 --expectSignal=1 &> initial_fit.log
echo 'impacts'
combineTool.py -M Impacts -d */$mass/workspace.root -m $mass --robustFit 1 --doFits --parallel 8 -t -1 --expectSignal=1 &> impacts.log
echo 'making json'
combineTool.py -M Impacts -d */$mass/workspace.root -m $mass -o impacts_$mass.json
echo 'making plots'
plotImpacts.py -i impacts_$mass.json -o impacts_$mass
cd -