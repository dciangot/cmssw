import FWCore.ParameterSet.Config as cms

process = cms.Process("BeamMonitor")

#----------------------------
# Event Source
#-----------------------------
process.load("DQM.Integration.test.inputsource_cfi")
process.EventStreamHttpReader.SelectEvents = cms.untracked.PSet(
    SelectEvents = cms.vstring('HLT_L1*',
                               'HLT_Jet*',
                               'HLT_*Cosmic*',
                               'HLT_HT*',
                               'HLT_MinBias_*',
                               'HLT_Physics*',
                               'HLT_ZeroBias_v2')
                              )

#--------------------------
# Filters
#--------------------------
# HLT Filter
process.load("HLTrigger.special.HLTTriggerTypeFilter_cfi")
# 0=random, 1=physics, 2=calibration, 3=technical
process.hltTriggerTypeFilter.SelectedTriggerType = 1


#----------------------------
# DQM Live Environment
#-----------------------------
process.load("DQM.Integration.test.environment_cfi")
process.dqmEnv.subSystemFolder = 'BeamMonitor'

import DQMServices.Components.DQMEnvironment_cfi
process.dqmEnvPixelLess = DQMServices.Components.DQMEnvironment_cfi.dqmEnv.clone()
process.dqmEnvPixelLess.subSystemFolder = 'BeamMonitor_PixelLess'

#----------------------------
# BeamMonitor
#-----------------------------
process.load("DQM.BeamMonitor.BeamMonitor_cff")
process.load("DQM.BeamMonitor.BeamMonitorBx_cff")
process.load("DQM.BeamMonitor.BeamMonitor_PixelLess_cff")
process.load("DQM.BeamMonitor.BeamConditionsMonitor_cff")
# NB that resetEveryNLumi means the number of lumis to use for the *running
# average*
process.dqmBeamMonitor.resetEveryNLumi = 5
process.dqmBeamMonitor.resetPVEveryNLumi = 5
process.dqmBeamMonitorBx.fitEveryNLumi = 30
process.dqmBeamMonitorBx.resetEveryNLumi = 30


#TriggerName for selecting pv for DIP publication, NO wildcard needed here
#it will pick all triggers which has these strings in theri name
process.dqmBeamMonitor.jetTrigger  = cms.untracked.vstring("HLT_ZeroBias_v",
                                                           "HLT_Jet300_v",
                                                           "HLT_QuadJet70_v")

process.dqmBeamMonitor.hltResults = cms.InputTag("TriggerResults","","HLT")


####  SETUP TRACKING RECONSTRUCTION ####

#-------------------------------------------------
# GEOMETRY
#-------------------------------------------------
process.load("Configuration.StandardSequences.Geometry_cff")

#-----------------------------
# Magnetic Field
#-----------------------------
#process.load('Configuration/StandardSequences/MagneticField_38T_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')

#--------------------------
# Calibration
#--------------------------
process.load("DQM.Integration.test.FrontierCondition_GT_cfi")


#-----------------------
#  Reconstruction Modules
#-----------------------
## Collision Reconstruction
process.load("Configuration.StandardSequences.RawToDigi_Data_cff")
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.load("RecoTracker.IterativeTracking.iterativeTk_cff")
#process.load("Configuration.GlobalRuns.reco_TLR_311X")

## Pixelless Tracking
process.load('RecoTracker/Configuration/RecoTrackerNotStandard_cff')
process.MeasurementTracker.pixelClusterProducer = cms.string("")

# Offline Beam Spot
process.load("RecoVertex.BeamSpotProducer.BeamSpot_cff")

## Offline PrimaryVertices
import RecoVertex.PrimaryVertexProducer.OfflinePrimaryVertices_cfi
process.offlinePrimaryVertices = RecoVertex.PrimaryVertexProducer.OfflinePrimaryVertices_cfi.offlinePrimaryVertices.clone()

#process.offlinePrimaryVertices.TrackLabel = cms.InputTag("ctfPixelLess")

process.dqmBeamMonitor.BeamFitter.TrackCollection = cms.untracked.InputTag('generalTracks')
process.dqmBeamMonitorBx.BeamFitter.TrackCollection = cms.untracked.InputTag('generalTracks')
process.offlinePrimaryVertices.TrackLabel = cms.InputTag("generalTracks")

## Not sure if these lines are needed Will remove later
#process.initialStepSeeds.ClusterCheckPSet.MaxNumberOfPixelClusters=2000
#process.newSeedFromPairs.ClusterCheckPSet.MaxNumberOfCosmicClusters=10000
#process.secTriplets.ClusterCheckPSet.MaxNumberOfPixelClusters=2000
#process.fifthSeeds.ClusterCheckPSet.MaxNumberOfCosmicClusters = 10000
#process.fourthPLSeeds.ClusterCheckPSet.MaxNumberOfCosmicClusters=10000


#---- replaces ----
process.initialStepSeeds.RegionFactoryPSet.ComponentName = 'GlobalRegionProducerFromBeamSpot' # was GlobalRegionProducer
#---- new parameters ----
process.initialStepSeeds.RegionFactoryPSet.RegionPSet.beamSpot = cms.InputTag("offlineBeamSpot")

#process.tracking = cms.Sequence(process.siPixelDigis
#                                *process.siStripDigis
#                                *process.trackerlocalreco
#                                *process.offlineBeamSpot
#                                *process.recopixelvertexing
#                                *process.ckftracks)

#process.tracking_pixelless = cms.Sequence(process.siPixelDigis
#                                           *process.siStripDigis
#                                           *process.trackerlocalreco
#                                           *process.offlineBeamSpot
#                                           *process.ctfTracksPixelLess)


#fast general track reco
process.iterTracking =cms.Sequence(process.InitialStep
                                  *process.LowPtTripletStep
                                  *process.PixelPairStep
                                  *process.DetachedTripletStep
                                  *process.MixedTripletStep
                                  *process.PixelLessStep
                                  *process.TobTecStep
                                  *process.generalTracks) 


process.tracking_FirstStep = cms.Sequence(process.siPixelDigis
                                         *process.siStripDigis
                                         *process.trackerlocalreco
                                         *process.offlineBeamSpot
                                         *process.recopixelvertexing
                                         *process.iterTracking)


#### END OF TRACKING RECONSTRUCTION ####





# Change Beam Monitor variables
if process.dqmSaver.producer.value() is "Playback":
  process.dqmBeamMonitor.BeamFitter.WriteAscii = False
  process.dqmBeamMonitor.BeamFitter.AsciiFileName = '/nfshome0/yumiceva/BeamMonitorDQM/BeamFitResults.txt'
  process.dqmBeamMonitor.BeamFitter.WriteDIPAscii = True
  process.dqmBeamMonitor.BeamFitter.DIPFileName = '/nfshome0/dqmdev/BeamMonitorDQM/BeamFitResults.txt'
else:
  process.dqmBeamMonitor.BeamFitter.WriteAscii = True
  process.dqmBeamMonitor.BeamFitter.AsciiFileName = '/nfshome0/yumiceva/BeamMonitorDQM/BeamFitResults.txt'
  process.dqmBeamMonitor.BeamFitter.WriteDIPAscii = True
  process.dqmBeamMonitor.BeamFitter.DIPFileName = '/nfshome0/dqmpro/BeamMonitorDQM/BeamFitResults.txt'
#process.dqmBeamMonitor.BeamFitter.SaveFitResults = False
#process.dqmBeamMonitor.BeamFitter.OutputFileName = '/nfshome0/yumiceva/BeamMonitorDQM/BeamFitResults.root'
  process.dqmBeamMonitorBx.BeamFitter.WriteAscii = True
  process.dqmBeamMonitorBx.BeamFitter.AsciiFileName = '/nfshome0/yumiceva/BeamMonitorDQM/BeamFitResults_Bx.txt'

#process.dqmBeamMonitor.BeamFitter.InputBeamWidth = 0.006
process.dqmBeamMonitor.PVFitter.minNrVerticesForFit = 25

## TKStatus
process.dqmTKStatus = cms.EDAnalyzer("TKStatus",
        BeamFitter = cms.PSet(
        DIPFileName = process.dqmBeamMonitor.BeamFitter.DIPFileName
        )
)



#--------------------------
# Path
#--------------------------
from DQM.Integration.test.environment_cfi import runType, runTypes
                               
process.dqmcommon = cms.Sequence(process.dqmEnv
                                *process.dqmSaver)

process.monitor = cms.Sequence(process.dqmBeamMonitor)

#process.monitor_pixelless = cms.Sequence(process.dqmBeamMonitor_pixelless
#                                        *process.dqmEnvPixelLess)

if (runType == runTypes.pp_run):

    print "Running pp"
    process.p = cms.Path(process.scalersRawToDigi
                         *process.dqmTKStatus
                         *process.hltTriggerTypeFilter
                         *process.dqmcommon
                         *process.tracking_FirstStep
                         *process.offlinePrimaryVertices
                         *process.monitor)



#--------------------------------------------------
# Heavy Ion Specific Fed Raw Data Collection Label
#--------------------------------------------------

if (runType == runTypes.hi_run):
    process.castorDigis.InputLabel = cms.InputTag("rawDataRepacker")
    process.csctfDigis.producer = cms.InputTag("rawDataRepacker")
    process.dttfDigis.DTTF_FED_Source = cms.InputTag("rawDataRepacker")
    process.ecalDigis.InputLabel = cms.InputTag("rawDataRepacker")
    process.ecalPreshowerDigis.sourceTag = cms.InputTag("rawDataRepacker")
    process.gctDigis.inputLabel = cms.InputTag("rawDataRepacker")
    process.gtDigis.DaqGtInputTag = cms.InputTag("rawDataRepacker")
    process.gtEvmDigis.EvmGtInputTag = cms.InputTag("rawDataRepacker")
    process.hcalDigis.InputLabel = cms.InputTag("rawDataRepacker")
    process.muonCSCDigis.InputObjects = cms.InputTag("rawDataRepacker")
    process.muonDTDigis.inputLabel = cms.InputTag("rawDataRepacker")
    process.muonRPCDigis.InputLabel = cms.InputTag("rawDataRepacker")
    process.scalersRawToDigi.scalersInputTag = cms.InputTag("rawDataRepacker")

#----------------------------
# Event Source
#-----------------------------
    process.load("DQM.Integration.test.inputsource_cfi")
    process.EventStreamHttpReader.SelectEvents =  cms.untracked.PSet(
     SelectEvents = cms.vstring(
        'HLT_HI*'
     )
    )


    process.dqmBeamMonitor.resetEveryNLumi = 5
    process.dqmBeamMonitor.resetPVEveryNLumi = 5

# HI only has one bunch
    process.dqmBeamMonitorBx.fitEveryNLumi = 50
    process.dqmBeamMonitorBx.resetEveryNLumi = 50


#TriggerName for selecting pv for DIP publication, NO wildcard needed here
#it will pick all triggers which has these strings in theri name
    process.dqmBeamMonitor.jetTrigger  = cms.untracked.vstring("HLT_HI*"
                                                               )

    process.dqmBeamMonitor.hltResults = cms.InputTag("TriggerResults","","HLT")


## Load Heavy Ion Sequence
    process.load("Configuration.StandardSequences.ReconstructionHeavyIons_cff") ## HI sequences

# Select events based on the pixel cluster multiplicity
    import  HLTrigger.special.hltPixelActivityFilter_cfi
    process.multFilter = HLTrigger.special.hltPixelActivityFilter_cfi.hltPixelActivityFilter.clone(
      inputTag  = cms.InputTag('siPixelClusters'),
      minClusters = cms.uint32(150),
      maxClusters = cms.uint32(50000)
      )

    process.filter_step = cms.Sequence( process.siPixelDigis
                                   *process.siPixelClusters
                                   #*process.multFilter
                                  )

    process.HIRecoForDQM = cms.Sequence( process.siPixelDigis
                                    *process.siPixelClusters
                                    *process.siPixelRecHits
                                    *process.offlineBeamSpot
                                    *process.hiPixelVertices
                                    *process.hiPixel3PrimTracks
                                   )

# use HI pixel tracking and vertexing
    process.dqmBeamMonitor.BeamFitter.TrackCollection = cms.untracked.InputTag('hiPixel3PrimTracks')
    process.dqmBeamMonitorBx.BeamFitter.TrackCollection = cms.untracked.InputTag('hiPixel3PrimTracks')
    process.dqmBeamMonitor.primaryVertex = cms.untracked.InputTag('hiSelectedVertex')
    process.dqmBeamMonitor.PVFitter.VertexCollection = cms.untracked.InputTag('hiSelectedVertex')

# Beamspot DQM options
    process.dqmBeamMonitor.OnlineMode = True                  ## in MC the LS are not ordered??
    process.dqmBeamMonitor.BeamFitter.MinimumTotalLayers = 3   ## using pixel triplets
    process.dqmBeamMonitorBx.BeamFitter.MinimumTotalLayers = 3   ## using pixel triplets

# make pixel vertexing less sensitive to incorrect beamspot
    process.hiPixel3ProtoTracks.RegionFactoryPSet.RegionPSet.originRadius = 0.2
    process.hiPixel3ProtoTracks.RegionFactoryPSet.RegionPSet.fixedError = 0.5
    process.hiSelectedProtoTracks.maxD0Significance = 100
    process.hiPixelAdaptiveVertex.TkFilterParameters.maxD0Significance = 100
    process.hiPixelAdaptiveVertex.useBeamConstraint = False
    process.hiPixelAdaptiveVertex.PVSelParameters.maxDistanceToBeam = 1.0

# Lower for HI
    process.dqmBeamMonitor.PVFitter.minNrVerticesForFit = 20
    process.dqmBeamMonitorBx.PVFitter.minNrVerticesForFit = 20


#--------------------------
# Scheduling
#--------------------------
#   process.phystrigger = cms.Sequence(process.hltTriggerTypeFilter
#                                      *process.gtDigis
#                                      *process.hltLevel1GTSeed)


    process.dqmcommon = cms.Sequence(process.dqmEnv
                                   *process.dqmSaver)


    process.monitor = cms.Sequence(process.dqmBeamMonitor
                                  #+process.dqmBeamMonitorBx
                                 )
    
    print "Running HI"
    process.hi = cms.Path(process.scalersRawToDigi
                        *process.dqmTKStatus
                        *process.hltTriggerTypeFilter
                        *process.filter_step
                        *process.HIRecoForDQM
                        *process.dqmcommon
                        *process.monitor)
