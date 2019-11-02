import pytest
import warnings
import numpy as np
import pandas as pd
import os
import mechanical_testing as mect

@pytest.fixture(scope="module")
def dimensions():
	length = 75.00E-3
	diameter = 10.00E-3
	return length, diameter

@pytest.fixture(scope="module")
def tensile(dimensions):
	return mect.TensileTest(
		'./test/data/tensile/tensile_steel_1045.csv',
		*dimensions,
	)

def test_read_csv(tensile):
	maxLocation = np.argmax(tensile.force)
	assert maxLocation                       ==               416
	assert tensile.time[maxLocation]         == pytest.approx(46.183,    rel=1E-12)
	assert tensile.displacement[maxLocation] == pytest.approx(0.0013913, rel=1E-12)
	assert tensile.force[maxLocation]        == pytest.approx(74715.3,   rel=1E-12)
	return

def test_dimensions(tensile, dimensions):
	length, diameter = dimensions
	assert tensile.length   == pytest.approx(length,                    rel=1E-10)
	assert tensile.diameter == pytest.approx(diameter,                  rel=1E-10)
	assert tensile.area     == pytest.approx(np.pi * (diameter**2) / 4, rel=1E-10)
	return

def test_strain_stress(tensile, dimensions):
	length, diameter = dimensions
	area = np.pi * (diameter**2) / 4
	maxLocation = np.argmax(tensile.stress)
	assert maxLocation                 ==               416
	assert tensile.strain[maxLocation] == pytest.approx(0.0013913/length, rel=1E-12)
	assert tensile.stress[maxLocation] == pytest.approx(74715.3/area,     rel=1E-12)
	return

def test_elastic_modulus(tensile):
	assert tensile.elasticModulus == pytest.approx(258.33E+9, rel=1E-2)
	return

def test_proportionalit_limit(tensile):
	assert tensile.proportionalityStrength == pytest.approx(462.43E+6, rel=1E-2)
	assert tensile.proportionalityStrain    == pytest.approx(0.17992E-2)
	return

def test_offset_yield_point(tensile):
	assert tensile.offsetYieldPoint(0.2E-2) == pytest.approx([0.50E-2, 765.22E+6], rel=1E-2)
	assert tensile.offsetYieldPoint(0.4E-2) == pytest.approx([0.73E-2, 849.64E+6], rel=1E-2)
	return

def test_yield_point(tensile):
	assert tensile.yieldStrain   == pytest.approx(0.50E-2,   rel=1E-2)
	assert tensile.yieldStrength == pytest.approx(765.22E+6, rel=1E-2)
	return

def test_ultimate_strength(tensile):
	assert tensile.ultimateStrain   == pytest.approx(1.86E-2,   rel=1E-2)
	assert tensile.ultimateStrength == pytest.approx(951.30E+6, rel=1E-2)
	return

def test_correct_yield_point(dimensions):
	tensile = mect.TensileTest(
		'./test/data/tensile/tensile_steel_1045_deformation_using_machine.csv',
		*dimensions,
	)
	assert tensile.proportionalityStrength  == pytest.approx(84.69E+6, rel=1E-2)
	assert tensile.proportionalityStrain    == pytest.approx( 1.05E-2, rel=1E-2)
	assert tensile.yieldStrain              == tensile.proportionalityStrain
	assert tensile.yieldStrength            == tensile.proportionalityStrength
	return

def test_elastic_behavior(tensile):
	assert tensile.elasticStrain[ 0] == pytest.approx(0.0)
	assert tensile.elasticStress[ 0] == pytest.approx(0.0)
	assert tensile.elasticStrain[-1] == pytest.approx(tensile.yieldStrain, rel=1E-2)
	assert tensile.elasticStress[-1] == pytest.approx(tensile.yieldStrength, rel=1E-2)
	return

def test_plastic_behavior(tensile):
	assert tensile.plasticStrain[ 0] == pytest.approx(tensile.yieldStrain, rel=1E-2)
	assert tensile.plasticStress[ 0] == pytest.approx(tensile.yieldStrength, rel=1E-2)
	assert tensile.plasticStrain[-1] == pytest.approx(tensile.ultimateStrain, rel=1E-2)
	assert tensile.plasticStress[-1] == pytest.approx(tensile.ultimateStrength, rel=1E-2)
	return

def test_necking_behavior(tensile):
	assert tensile.neckingStrain[ 0] == pytest.approx(tensile.ultimateStrain, rel=1E-2)
	assert tensile.neckingStress[ 0] == pytest.approx(tensile.ultimateStrength, rel=1E-2)
	assert tensile.neckingStrain[-1] == pytest.approx(tensile.strain[-1], rel=1E-10)
	assert tensile.neckingStress[-1] == pytest.approx(tensile.stress[-1], rel=1E-10)
	return

def test_resilience_modulus(tensile):
	assert tensile.resilienceModulus == pytest.approx(2.464E+6, rel=1E-3)
	return

def test_toughness_modulus(tensile):
	assert tensile.toughnessModulus == pytest.approx(1.916E+7, rel=1E-3)
	return

def test_real_curve(tensile):
	ultimateLocation = np.argmax(tensile.realStress)
	ultimateRealStrain = tensile.realStrain[ultimateLocation]
	ultimateRealStress = tensile.realStress[ultimateLocation]
	assert ultimateRealStrain == pytest.approx(1.90E-2,   rel=1E-2)
	assert ultimateRealStress == pytest.approx(969.25E+6, rel=1E-2)
	return

def test_hardening(tensile):
	assert tensile.strengthCoefficient == pytest.approx(1977.97E+6, rel=1E-4)
	assert tensile.strainHardeningExponent == pytest.approx(1.712E-1, rel=1E-4)
	return

def test_properties_summary(tensile):
	# Compilation of all the values in the tests above.
	materialProperties = pd.DataFrame(
			columns = ['Property', 'Value', 'Unit'],
			data = [
				['Elastic Modulus',           258.33E+9,  'Pa'   ],
				['Proportionality Strain',    0.17992E-2, '-'    ],
				['Proportionality Strength',  462.43E+6,  'Pa'   ],
				['Yield Strain',              0.50E-2,    '-'    ],
				['Yield Strength',            765.22E+6,  'Pa'   ],
				['Ultimate Strain',           1.86E-2,    '-'    ],
				['Ultimate Strength',         951.30E+6,  'Pa'   ],
				['Resilience Modulus',        2.464E+6,   'J/m^3'],
				['Toughness Modulus',         1.916E+7,   'J/m^3'],
				['Strength Coefficient',      1977.97E+6, 'Pa'   ],
				['Strain Hardening Exponent', 1.712E-1,   '-'    ],
			],
		)
	summaryOfProperties = tensile.summaryOfProperties()
	assert (summaryOfProperties['Property'] == materialProperties['Property']).all()
	assert np.array(summaryOfProperties['Value']) == pytest.approx(np.array(materialProperties['Value']), rel=1E-2)
	assert (summaryOfProperties['Unit'] == materialProperties['Unit']).all()
	return

def test_save_summary_of_properties(tensile):
	fileName = '.summaryOfProperties.csv'
	tensile.saveSummaryOfProperties(fileName)
	assert os.path.isfile(fileName)
	os.remove(fileName)
	return

def test_plot(tensile):
	# Since it is a visual inspection, no assertion
	# will be done. Instead, the output files will
	# be placed in a specific folder for manual
	# inspection.
	saveFolder = 'test/data/plots/'
	os.makedirs(saveFolder, exist_ok=True)
	fileName = 'steel_1045.png'
	filePath = saveFolder + fileName
	title = 'Steel 1045'
	tensile.plot(title, filePath)
	assert os.path.isfile(filePath)
	warnings.warn('Check the quality of the file \"{}\" manually.'.format(filePath))
	return

def test_real_plot(tensile):
	# Since it is a visual inspection, no assertion
	# will be done. Instead, the output files will
	# be placed in a specific folder for manual
	# inspection.
	saveFolder = 'test/data/plots/'
	os.makedirs(saveFolder, exist_ok=True)
	fileName = 'steel_1045_real_curve.png'
	filePath = saveFolder + fileName
	title = 'Steel 1045'
	tensile.plotRealCurve(title, filePath)
	assert os.path.isfile(filePath)
	warnings.warn('Check the quality of the file \"{}\" manually.'.format(filePath))
	return