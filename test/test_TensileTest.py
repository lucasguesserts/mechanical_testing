import pytest
import numpy as np
import mechanical_testing as mect

@pytest.fixture(scope="module")
def dimensions():
	length = 75.00E-3
	diameter = 10.00E-3
	return length, diameter

@pytest.fixture(scope="module")
def tensile(dimensions):
	print(dimensions)
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
	assert tensile.length   == pytest.approx(length, rel=1E-10)
	assert tensile.diameter == pytest.approx(diameter, rel=1E-10)
	assert tensile.area     == pytest.approx(np.pi * (diameter**2) / 4, rel=1E-10)
	return