import numpy as np
import pandas as pd
import scipy.optimize
import copy

class TensileTest:
	def __init__(self, file, length, diameter):
		self._readFromFile(file)
		self._defineDimensions(length, diameter)
		self._defineStrainStress()
		self._defineElasticModulusAndProportionalityLimit()
		self._defineYieldStrength()
		return

	def _readFromFile(self, file):
		df = pd.read_csv(filepath_or_buffer=file)
		self.force        = copy.deepcopy(np.array(df['force']).flatten())
		self.displacement = copy.deepcopy(np.array(df['displacement']).flatten())
		self.time         = copy.deepcopy(np.array(df['time']).flatten())
		del df
		return

	def _defineDimensions(self, length, diameter):
		self.length = length
		self.diameter = diameter
		self.area = np.pi * (diameter**2) / 4
		return

	def _defineStrainStress(self):
		self.strain = self.displacement / self.length
		self.stress = self.force / self.area
		return

	def _defineElasticModulusAndProportionalityLimit(self):
		# Find proportionality limit location
		# TODO: substitute this piece of code
		# by calling scipy.optimize.brute
		minimumResidual = +np.infty
		for length in np.arange(10, len(self.stress)):
			polynomial, fullResidual = np.polyfit(
				x = self.strain[:length],
				y = self.stress[:length],
				deg = 1,
				cov = True,
			)
			residual = np.sqrt(np.diag(fullResidual)[0])
			if residual < minimumResidual:
				minimumResidual = residual
				proportionalityLimitLocation = length
				angularCoefficient = polynomial[0]
		# Set values
		self.proportionalityStrength      = self.stress[proportionalityLimitLocation]
		self.propotionalityStrain         = self.strain[proportionalityLimitLocation]
		self.elasticModulus               = angularCoefficient
		return

	def offsetYieldPoint(self, n):
		elasticLine = lambda n: self.elasticModulus * ( self.strain - n )
		intersection = np.argwhere(self.stress - elasticLine(n) < 0).flatten()[0]
		return self.strain[intersection], self.stress[intersection]

	def _defineYieldStrength(self):
		self.yieldStrain, self.yieldStrength = self.offsetYieldPoint(0.2E-2)
		return