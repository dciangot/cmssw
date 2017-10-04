# input dataset

TASK_LIST=(SPSJJ
SPSpp
WZ
SPSmm
DPS
WZTo3LNu
ZZTo4L
WWW
TTJets_SingleLeptFromTbar
TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8
WGToLNuG
WWTo2L2Nu
)

INPUT_LIST=(/WpWpJJ_EWK-QCD_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM
/WpWpJJ_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM
/WZ_TuneCUETP8M1_13TeV-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM
/WmWmJJ_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v2/MINIAODSIM
/WW_DoubleScattering_13TeV-pythia8/RunIISpring16MiniAODv1-PUSpring16_80X_mcRun2_asymptotic_2016_v3-v1/MINIAODSIM
/WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM
/ZZTo4L_13TeV_powheg_pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM
/WWW_4F_TuneCUETP8M1_13TeV-amcatnlo-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM
/TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM
/TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM
/WGToLNuG_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM
/WWTo2L2Nu_DoubleScattering_13TeV-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM)


k=0
for TASK in ${TASK_LIST[*]};do
INPUT_DATASET=${INPUT_LIST[k]}
k=$((k+1))

# iterator number and folder init
i=0
JOB_FOLDER=jobs
OUTPUT_FOLDER=/eos/user/d/dciangot/NTuples_v2/$TASK
RESUBMIT=$1

# if folder exists don't submit again
if [ ! -d "$OUTPUT_FOLDER" ] || [[ $RESUBMIT = "resubmit" ]]; then

if [[ $RESUBMIT = "resubmit" ]]; then 
echo "RESUBMITTING"
JOB_FOLDER=${JOB_FOLDER}_resubmit
rm -fr ${JOB_FOLDER}/*$TASK*
fi

mkdir -p $JOB_FOLDER
mkdir -p $OUTPUT_FOLDER

echo "SUBMITTING: $TASK"
echo "Collecting information for job creation"

for file in `dasgoclient -query="file dataset=$INPUT_DATASET" | sed -e "s%\/%\\\\\/%g"`; do

i=$((i+1))

if [ ! -e $OUTPUT_FOLDER/tree${i}.root ]; then
#echo "JOB: $file"
# prepar job
echo "cp example_autofill.py $JOB_FOLDER/${TASK}${i}.py"
cp example_autofill.py $JOB_FOLDER/${TASK}${i}.py
sed -i -e "s/files = testfiles/files = \[\"root:\/\/xrootd.ba.infn.it\/$file\"\]/" $JOB_FOLDER/${TASK}${i}.py
sed -i -e "s/tree.root/tree${i}.root/" $JOB_FOLDER/${TASK}${i}.py
sed -i -e "s/nEvents=.*/nEvents=100000000000000000000)/" $JOB_FOLDER/${TASK}${i}.py
sed -i -e "s/Looper( 'Loop'/Looper( '${TASK}${i}'/" $JOB_FOLDER/${TASK}${i}.py

echo "#!/bin/bash
cd $PWD 
export SCRAM_ARCH=slc6_amd64_gcc493
export X509_USER_PROXY=/afs/cern.ch/user/d/dciangot/proxy
eval \`scram runtime -sh\`

cd -

python ${TASK}${i}.py

" > $JOB_FOLDER/${TASK}${i}.sh

chmod +x $JOB_FOLDER/${TASK}${i}.sh

# prepare stageout script
#echo "prepare stageout script"
echo "#!/bin/bash
mv ${TASK}${i}/tree${i}.root $OUTPUT_FOLDER/tree${i}.root
" > $JOB_FOLDER/copy_${TASK}${i}.sh

chmod +x $JOB_FOLDER/copy_${TASK}${i}.sh

else

echo "${i} CHECKED, skipping"

fi
done

# submit job
echo "submit task $TASK"

echo "
executable            = $JOB_FOLDER/\$Fn(filename).sh
arguments             = \$(ClusterID) \$(ProcId)
output                = /dev/null
error                 = /dev/null
log                   = condor.log
transfer_input_files    = $JOB_FOLDER/copy_\$Fn(filename).sh, $JOB_FOLDER/\$Fn(filename).py
+PostCmd  = \"copy_\$Fn(filename).sh\"
+JobFlavour             = \"longlunch\"
queue filename matching ($JOB_FOLDER/${TASK}*.sh)
" > $JOB_FOLDER/${TASK}.sub

echo "submit jobs"
condor_submit $JOB_FOLDER/${TASK}.sub 

else
echo "DIR $OUTPUT_FOLDER ALREADY EXISTS, SKIPPING"

fi

done
