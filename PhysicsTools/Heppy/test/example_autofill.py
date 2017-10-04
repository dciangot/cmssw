#! /usr/bin/env python
import ROOT
import PhysicsTools.HeppyCore.framework.config as cfg

# The content of the output tree is defined here
# the definitions of the NtupleObjects are located under PhysicsTools/Heppy/pythonanalyzers/objects/autophobj.py
 
from PhysicsTools.Heppy.analyzers.core.AutoFillTreeProducer  import * 
treeProducer= cfg.Analyzer(
	class_object=AutoFillTreeProducer, 
	verbose=True, 
	vectorTree = True,
        #here the list of simple event variables (floats, int) can be specified
        globalVariables = [
             NTupleVariable("nPU",  lambda ev: ev.nPU, float, help="PU"),
        ],
        #here one can specify compound objects 
        globalObjects = {
            "met"    : NTupleObject("met",     metType, help="PF E_{T}^{miss}, after default type 1 corrections"),
        },
	    collections = {
		#standard dumping of objects
   	        "selectedLeptons" : NTupleCollection("leptons", leptonType, 8, help="Leptons after the preselection"),
	        "cleanJets"       : NTupleCollection("Jet",     jetType, 8, help="Cental jets after full selection and cleaning, sorted by b-tag"),
		#dump of gen objects
            "genleps"         : NTupleCollection("GenLep",  genParticleWithMotherId, 6, help="Generated leptons from W/Z decays"),
            "genVBosons"         : NTupleCollection("GenBosons",  genParticleWithMotherId, 6, help="Generated W/Z"),
            "gennus"         : NTupleCollection("GenNus",  genParticleWithMotherId, 6, help="Generated neutrinos"),

	}
	)

# Import standard analyzers and take their default config
from PhysicsTools.Heppy.analyzers.objects.LeptonAnalyzer import LeptonAnalyzer
LepAna = LeptonAnalyzer.defaultConfig
from PhysicsTools.Heppy.analyzers.objects.VertexAnalyzer import VertexAnalyzer
VertexAna = VertexAnalyzer.defaultConfig
from PhysicsTools.Heppy.analyzers.objects.TauAnalyzer import TauAnalyzer
TauAna = TauAnalyzer.defaultConfig
from PhysicsTools.Heppy.analyzers.objects.JetAnalyzer import JetAnalyzer
JetAna = JetAnalyzer.defaultConfig
from PhysicsTools.Heppy.analyzers.gen.LHEAnalyzer import LHEAnalyzer 
LHEAna = LHEAnalyzer.defaultConfig
from PhysicsTools.Heppy.analyzers.gen.GeneratorAnalyzer import GeneratorAnalyzer 
GenAna = GeneratorAnalyzer.defaultConfig
from PhysicsTools.Heppy.analyzers.objects.METAnalyzer import METAnalyzer
METAna = METAnalyzer.defaultConfig
from PhysicsTools.Heppy.analyzers.core.PileUpAnalyzer import PileUpAnalyzer
PUAna = PileUpAnalyzer.defaultConfig
from PhysicsTools.Heppy.analyzers.core.TriggerBitAnalyzer import TriggerBitAnalyzer
FlagsAna = TriggerBitAnalyzer.defaultEventFlagsConfig

# Configure trigger bit analyzer
from PhysicsTools.Heppy.analyzers.core.TriggerBitAnalyzer import TriggerBitAnalyzer
TrigAna= cfg.Analyzer(
    verbose=False,
    class_object=TriggerBitAnalyzer,
    #grouping several paths into a single flag
    # v* can be used to ignore the version of a path
    triggerBits={
    'ELE':["HLT_Ele23_Ele12_CaloId_TrackId_Iso_v*","HLT_Ele32_eta2p1_WP85_Gsf_v*","HLT_Ele32_eta2p1_WP85_Gsf_v*"],
    'MU': ["HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v*","HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v*","HLT_IsoTkMu24_eta2p1_IterTrk02_v*","HLT_IsoTkMu24_IterTrk02_v*"],
    },
#   processName='HLT',
#   outprefix='HLT'
    #setting 'unrollbits' to true will not only store the OR for each set of trigger bits but also the individual bits
    #caveat: this does not unroll the version numbers
    unrollbits=True 
    )

#replace some parameters
LepAna.loose_muon_pt = 10
#LepAna.ele_tightId = "MVA"
LepAna.doMiniIsolation = True
LepAna.do_mc_match = False
JetAna.do_mc_match = False
JetAna.smearJets = False
JetAna.attachNeutrinos = False
GenAna.makeAllGenParticles = False

#sequence = [LHEAna,FlagsAna, GenAna, PUAna,TrigAna,VertexAna,LepAna,TauAna,PhoAna,JetAna,METAna,treeProducer]
sequence = [FlagsAna, GenAna, PUAna,TrigAna,VertexAna,LepAna,JetAna,METAna,treeProducer]

#use tfile service to provide a single TFile to all modules where they
#can write any root object. If the name is 'outputfile' or the one specified in treeProducer
#also the treeProducer uses this file
from PhysicsTools.HeppyCore.framework.services.tfile import TFileService 
output_service = cfg.Service(
      TFileService,
      'outputfile',
      name="outputfile",
      fname='tree.root',
      option='recreate'
    )

# the following two lines are just for automatic testing
# they are not needed for running on your own samples
testfiles=["root://xrootd.ba.infn.it//store/mc/RunIISpring16MiniAODv1/WW_DoubleScattering_13TeV-pythia8/MINIAODSIM/PUSpring16_80X_mcRun2_asymptotic_2016_v3-v1/50000/045F7DD1-D909-E611-9D15-B499BAAC0270.root"]

sample = cfg.MCComponent(
#specify the file you want to run on
    # files = ["/scratch/arizzi/Hbb/CMSSW_7_2_2_patch2/src/VHbbAnalysis/Heppy/test/ZLL-8A345C56-6665-E411-9C25-1CC1DE04DF20.root"],
    files = testfiles,
    #files = ["root://xrootd.ba.infn.it//store/mc/RunIISpring16MiniAODv1/WW_DoubleScattering_13TeV-pythia8/MINIAODSIM/PUSpring16_80X_mcRun2_asymptotic_2016_v3-v1/50000/045F7DD1-D909-E611-9D15-B499BAAC0270.root"],
    name="SingleSample", isMC=True,isEmbed=False
    )

# the following is declared in case this cfg is used in input to the heppy.py script
from PhysicsTools.HeppyCore.framework.eventsfwlite import Events
selectedComponents = [sample]
config = cfg.Config( components = selectedComponents,
                     sequence = sequence,
                     services = [output_service],  
                     events_class = Events)

# and the following runs the process directly if running as with python filename.py  
if __name__ == '__main__':
    from PhysicsTools.HeppyCore.framework.looper import Looper 
    looper = Looper( 'Loop', config, nPrint = 5,nEvents=-1) 
    looper.loop()
    looper.write()
