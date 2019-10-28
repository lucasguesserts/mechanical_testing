import numpy as np
import pandas as pd
import scipy.integrate
import matplotlib.pyplot as plt
import copy

plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 12

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
		self.proportionalityStrain        = self.strain[proportionalityLimitLocation]
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

	def summaryOfProperties(self):
		return pd.DataFrame(
			columns = ['Property', 'Value', 'Unit'],
			data = [
				['Elastic Modulus',           self.elasticModulus,          'Pa'   ],
				['Proportionality Strain',    self.proportionalityStrain,   '-'    ],
				['Proportionality Strength',  self.proportionalityStrength, 'Pa'   ],
				['Yield Strain',              self.yieldStrain,             '-'    ],
				['Yield Strength',            self.yieldStrength,           'Pa'   ],
				['Ultimate Strain',           self.ultimateStrain,          '-'    ],
				['Ultimate Strength',         self.ultimateStrength,        'Pa'   ],
				['Resilience Modulus',        self.resilienceModulus,       'J/m^3'],
				['Toughness Modulus',         self.toughnessModulus,        'J/m^3'],
				['Strength Coefficient',      self.strengthCoefficient,     'Pa'   ],
				['Strain Hardening Exponent', self.strainHardeningExponent, '-'    ],
			],
		)

	def saveSummaryOfProperties(self, fileName):
		self.summaryOfProperties().to_csv(
			path_or_buf = fileName,
			index = False,
		)
		return

	def plot(self, title, fileName):
		fig = plt.figure(figsize=(8,8))
		ax = fig.add_subplot(1,1,1)
		# Relevant Regions
		ax.plot(100*self.elasticStrain, self.elasticStress/1E+6, linestyle='-', color='b', label='Elastic\nRegion')
		ax.plot(100*self.plasticStrain, self.plasticStress/1E+6, linestyle='-', color='y', label='Plastic\nRegion')
		ax.plot(100*self.neckingStrain, self.neckingStress/1E+6, linestyle='-', color='r', label='Necking\nRegion')
		# Relevant Points
		ax.plot(100*self.proportionalityStrain, self.proportionalityStrength/1E+6, color='k', marker='o', linestyle=None, label='Proportionality\nLimit')
		ax.plot(100*self.yieldStrain, self.yieldStrength/1E+6, color='k', marker='x', linestyle=None, label='Yield\nStrength')
		ax.plot(100*self.ultimateStrain, self.ultimateStrength/1E+6, color='k', marker='*', linestyle=None, label='Ultimate\nStrength')
		# Curve Fit
		ax.plot(100*self.elasticStrain, np.polyval([self.elasticModulus,0], self.elasticStrain)/1E+6, linestyle='-.', color='gray', label='Elastic\nCurve Fit')
		ax.plot(100*self.plasticStrain, self.strengthCoefficient*self.plasticStrain**self.strainHardeningExponent/1E+6, linestyle='--', color='gray', label='Hollomon\'s\nCurve Fit')
		# Layout
		ax.set_xlim([0, 1.45*np.amax(100*self.strain)])
		ax.set_ylim([0, 1.1*self.ultimateStrength/1E+6])
		ax.set_xlabel('Strain [%]')
		ax.set_ylabel('Stress [MPa]')
		ax.legend(loc='upper right')
		ax.set_title(title)
		ax.grid(which='major', axis='x', linestyle='--', color='gray', alpha=0.75)
		ax.grid(which='minor', axis='x', linestyle='--', color='gray', alpha=0.50)
		ax.grid(which='major', axis='y', linestyle='--', color='gray', alpha=0.75)
		ax.grid(which='minor', axis='y', linestyle='--', color='gray', alpha=0.50)
		# Save
		fig.tight_layout()
		fig.savefig(fileName)
		plt.close(fig)
		return