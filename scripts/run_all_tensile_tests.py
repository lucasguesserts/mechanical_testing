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

# Files and dimensions
files_lengths_diameters = [
    ['compression_polyacetal', 40.00E-3, 40.00E-3],
    ['tensile_steel_1045', 75.00E-3, 10.00E-3],
    ['tensile_steel_4130', 75.00E-3, 10.00E-3],
    ['compression_steel_1045', 25.00E-3, 10.00E-3],
    ['tensile_steel_1045_deformation_using_machine', 75.00E-3, 10.00E-3],
    ['tensile_steel_4130_deformation_using_machine', 75.00E-3, 10.00E-3],
]

# Tensile test analysis
for rootName, length, diameter in files_lengths_diameters:
    tensile = mect.TensileTest(experimentalDataDir+rootName+'.csv', length, diameter)
    tensile.plot(rootName, saveDir+rootName+'.png')
    tensile.plotRealCurve(rootName, saveDir+rootName+'_real_curve'+'.png')
    tensile.saveSummaryOfProperties(saveDir+rootName+'.csv')