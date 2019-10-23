import pytest
import numpy as np
import mechanical_testing as mect

def test_read_csv():
	tensile = mect.TensileTest('./test/data/tensile/tensile_steel_1045.csv')
	maxLocation = np.argmax(tensile.force)
	assert maxLocation                       ==               416
	assert tensile.time[maxLocation]         == pytest.approx(46.183,    rel=1E-12)
	assert tensile.displacement[maxLocation] == pytest.approx(0.0013913, rel=1E-12)
	assert tensile.force[maxLocation]        == pytest.approx(74715.3,   rel=1E-12)
	return
