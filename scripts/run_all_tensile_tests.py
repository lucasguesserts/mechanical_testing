import sys
import os
sys.path.append("../")
import mechanical_testing as mect

# Setup
length = 75.00E-3 # m
diameter = 10.00E-3 # m
saveDir = 'run_all_tensile_tests/'
experimentalDataDir = '../test/data/tensile/'

# Save directory
os.makedirs(saveDir, exist_ok=True)

# Files
experimentFiles = os.listdir(experimentalDataDir)

# Tensile test analysis
for experimentFile in experimentFiles:
    rootName = experimentFile.split('/')[-1].replace('.csv','')
    tensile = mect.TensileTest(experimentalDataDir+experimentFile, length, diameter)
    tensile.plot(rootName, saveDir+rootName+'.png')
    tensile.plotRealCurve(rootName, saveDir+rootName+'_real_curve'+'.png')
    tensile.saveSummaryOfProperties(saveDir+rootName+'.csv')