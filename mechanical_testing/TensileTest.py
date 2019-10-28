import numpy as np
import pandas as pd
import scipy.integrate
import copy

class TensileTest:
	def __init__(self, file, length, diameter):
		self._readFromFile(file)
		self._defineDimensions(length, diameter)
		self._defineEngineeringCurve()
		self._defineRealCurve()
		self._defineElasticModulusAndProportionalityLimit()
		self._defineYieldStrength()
		self._defineUltimateStrength()
		self._defineElasticBehavior()
		self._definePlasticBehavior()
		self._defineNeckingBehavior()
		self._defineResilienceModulus()
		self._defineToughnessModulus()
		self._defineHardening()
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

	def _defineEngineeringCurve(self):
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

	def _defineUltimateStrength(self):
		ultimateLocation      = np.argmax(self.stress)
		self.ultimateStrain   = self.strain[ultimateLocation]
		self.ultimateStrength = self.stress[ultimateLocation]
		return

	def _defineElasticBehavior(self):
		elasticBehavior = (self.strain < self.yieldStrain)
		self.elasticStrain = self.strain[elasticBehavior]
		self.elasticStress = self.stress[elasticBehavior]
		return

	def _definePlasticBehavior(self):
		plasticBehavior = (self.yieldStrain < self.strain) & (self.strain < self.ultimateStrain)
		self.plasticStrain = self.strain[plasticBehavior]
		self.plasticStress = self.stress[plasticBehavior]
		return

	def _defineNeckingBehavior(self):
		neckingBehavior = (self.ultimateStrain < self.strain)
		self.neckingStrain = self.strain[neckingBehavior]
		self.neckingStress = self.stress[neckingBehavior]
		return

	def _defineResilienceModulus(self):
		self.resilienceModulus = scipy.integrate.trapz(x=self.elasticStrain, y=self.elasticStress)
		return

	def _defineToughnessModulus(self):
		self.toughnessModulus = scipy.integrate.trapz(x=self.strain, y=self.stress)
		return

	@staticmethod
	def _engineering2real(strain, stress):
		realStrain = np.log(1 + strain)
		realStress = stress * (1 + strain)
		return realStrain, realStress

	def _defineRealCurve(self):
		self.realStrain, self.realStress = TensileTest._engineering2real(
			self.strain,
			self.stress
		)
		return

	def _defineHardening(self):
		hollomons_equation = lambda strain, K, n: K * strain**n
		realStrain, realStress = TensileTest._engineering2real(self.plasticStrain, self.plasticStress)
		(K, n), _ = scipy.optimize.curve_fit(
			hollomons_equation,
			xdata = realStrain,
			ydata = realStress,
			p0 = [124.6E+6, 0.19] # typical values
		)
		self.strengthCoefficient     = K
		self.strainHardeningExponent = n
		return