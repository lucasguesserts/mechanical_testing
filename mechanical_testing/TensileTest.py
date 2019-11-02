import numpy as np
import pandas as pd
import scipy.integrate
import matplotlib.pyplot as plt
import copy
import warnings

plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 12

class TensileTest:
	'''Process tensile testing data.

	Load a tensile test data and process it
	in order to deliver the material
	properties.

	Warning
	-------
	All values are meant to be in the SI
	units. Since no unit conversion is made,
	the input data has to be in the SI
	units.

	Attributes
	----------
	originalFile : str
		Path to the file from which the data was read.
	force : numpy.ndarray
		Force data from the tensile test.
	displacement : numpy.ndarray
		Displacement data from the tensile test.
	time : numpy.ndarray
		Time instant data from the tensile test.
	length : float
		Gage length of the specimen.
	diameter : float
		Diameter of the specimen.
	area : float
		Cross section area of the specimen.
		:math:`A = \dfrac{\pi \ D}{4}`
		being :math:`D` the diameter of the
		specimen.
	strain : numpy.ndarray
		Strain data of the tensile test.
		:math:`\varepsilon = \dfrac{l - l_0}{l_0} = \dfrac{d}{l_0}`
		being :math:`l_0` the initial length.
	stress : numpy.ndarray
		Stress data of the tensile test.
		:math:`\sigma = \dfrac{F}{A}`
		being :math:`F` the force and
		:math:`A` the cross section area.
	realStrain : numpy.ndarray
		Strain for the real curve.
		:math:`\varepsilon_{real} = ln(1 + \varepsilon).
	realStress : numpy.ndarray
		Stress for the real curve.
		:math:`\sigma_{real} = \sigma \ (1 + \varepsilon).
	proportionalityStrain, proportionalityStrength : float
		Stress and strain values at the proportionality
		limit point.
	yieldStrain, yieldStrength : float
		Stress and strain values at the yield point.
	ultimateStrain, ultimateStrength : float
		Stress and strain values at the ultimate point.
	strengthCoefficient, strainHardeningExponent : float
		Those are coefficients for the Hollomon's
		equation during the plastic deformation. It
		represents the hardening behavior of the
		material.
		Hollomon's equation:
		:math:`\sigma = K \ \varepsilon^{n}`
		being :math:`K` the strength coefficient
		and  :math:`n` the strain hardening exponent.
	elasticStrain, elasticStress : numpy.ndarray
		Strain and stress data when the material
		behaves elastically.
	plasticStrain, plasticStress : numpy.ndarray
		Strain and stress data when the material
		behaves plastically.
	neckingStrain, neckingStress : numpy.ndarray
		Strain and stress data when the
		necking starts at the material.
	elasticModulus : float
		Elastic modulus value.
	resilienceModulus : float
		Resilience modulus value. It is the energy
		which the material absorbs per unit of volume
		during its elastic deformation.
	toughnessModulus : float
		Resilience modulus value. It is the energy
		which the material absorbs per unit of volume
		until its failure.

	See Also
	--------
	[Tensile testing wikipedia page](https://en.wikipedia.org/wiki/Tensile_testing)
	[Stress-Strain curve wikipedia page](https://en.wikipedia.org/wiki/Stress%E2%80%93strain_curve)

	Notes
	-----
	| Symbol | Description | Definition |
	| --- | --- | --- |
	| :math:`[F]`                          | force                               | input                                                               |
	| :math:`[d]`                          | displacement                        | input                                                               |
	| :math:`[t]`                          | time                                | input                                                               |
	| :math:`l_0`                          | specimen length                     | input                                                               |
	| :math:`D`                            | specimen diameter                   | input                                                               |
	| :math:`A`                            | specimen cross section area         | :math:`A = \dfrac{\pi \ D^2}{4}`                                    |
	| :math:`[\varepsilon]`                | strain                              | :math:`\varepsilon = \dfrac{l - l_0}{l_0} = \dfrac{d}{l_0}`         |
	| :math:`[\sigma]`                     | stress                              | :math:`\sigma = \dfrac{F}{A}`                                       |
	| :math:`[\varepsilon_r]`              | real strain                         | :math:`\varepsilon_r = ln(1 + \varepsilon)`                         |
	| :math:`[\sigma_r]`                   | real stress                         | :math:`\sigma_r = \sigma \ (1 + \varepsilon)`                       |
	| :math:`\varepsilon_{pr},\sigma_{pr}` | proportionality strain and strength | Algorithm defined                                                   |
	| :math:`\varepsilon_y,\sigma_y`       | yield strain and strength           | Algorithm defined                                                   |
	| :math:`\varepsilon_u,\sigma_u`       | ultimate strain and strength        | Algorithm defined                                                   |
	| :math:`K`                            | strength coefficient                | Algorithm defined                                                   |
	| :math:`n`                            | strain hardening exponent           | Algorithm defined                                                   |
	| :math:`[\varepsilon_e]`              | elastic strain                      | :math:`[\varepsilon][                \varepsilon < \varepsilon_y]`  |
	| :math:`[\sigma_p]`                   | plastic stress                      | :math:`[\sigma     ][                \varepsilon < \varepsilon_y]`  |
	| :math:`[\varepsilon_n]`              | necking strain                      | :math:`[\varepsilon][\varepsilon_y < \varepsilon < \varepsilon_u]`  |
	| :math:`[\sigma_e]`                   | elastic stress                      | :math:`[\sigma     ][\varepsilon_y < \varepsilon < \varepsilon_u]`  |
	| :math:`[\varepsilon_p]`              | plastic strain                      | :math:`[\varepsilon][\varepsilon_u < \varepsilon                ]`  |
	| :math:`[\sigma_n]`                   | necking stress                      | :math:`[\sigma     ][\varepsilon_u < \varepsilon                ]`  |
	| :math:`E`                            | elastic modulus                     | :math:`\sigma = E \ \varepsilon`                                    |
	| :math:`U_r`                          | resilience modulus                  | :math:`\displaystyle\int\limits_{[\varepsilon_e]}\sigma \mathrm{d}` |
	| :math:`U_t`                          | toughness modulus                   | :math:`\displaystyle\int\limits_{[\varepsilon]}\sigma \mathrm{d}`   |
	'''
	def __init__(self, file, length, diameter):
		self._readFromFile(file)
		self._defineDimensions(length, diameter)
		self._defineEngineeringCurve()
		self._defineRealCurve()
		self._defineElasticModulusAndProportionalityLimit()
		self._defineYieldStrength()
		self._defineUltimateStrength()
		self._correctYieldStrength()
		self._defineElasticBehavior()
		self._definePlasticBehavior()
		self._defineNeckingBehavior()
		self._defineResilienceModulus()
		self._defineToughnessModulus()
		self._defineHardening()
		return

	def _readFromFile(self, file):
		df = pd.read_csv(filepath_or_buffer=file)
		self.originalFile = file
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

	def _correctYieldStrength(self):
		if self.yieldStrain > self.ultimateStrain:
			self.yieldStrain   = self.proportionalityStrain
			self.yieldStrength = self.proportionalityStrength
			warnings.warn('Yield strength corrected in file \"{:s}\"'.format(self.originalFile))
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

	def plotRealCurve(self, title, fileName):
		fig = plt.figure(figsize=(8,8))
		ax = fig.add_subplot(1,1,1)
		def ax_plot(strain, stress, **kwargs):
			realStrain, realStress = TensileTest._engineering2real(strain, stress)
			ax.plot(100*realStrain, realStress/1E+6, **kwargs)
			return
		# Engineering Curve
		ax.plot(100*self.strain, self.stress/1E+6, linestyle=':', color='k', alpha=0.75, label='Engineering\nCurve')
		# Relevant Regions
		ax_plot(self.elasticStrain, self.elasticStress, linestyle='-', color='b', label='Elastic\nRegion')
		ax_plot(self.plasticStrain, self.plasticStress, linestyle='-', color='y', label='Plastic\nRegion')
		ax_plot(self.neckingStrain, self.neckingStress, linestyle='-', color='r', label='Necking\nRegion')
		# Relevant Points
		ax_plot(self.proportionalityStrain, self.proportionalityStrength, color='k', marker='o', linestyle=None, label='Proportionality\nLimit')
		ax_plot(self.yieldStrain, self.yieldStrength, color='k', marker='x', linestyle=None, label='Yield\nStrength')
		ax_plot(self.ultimateStrain, self.ultimateStrength, color='k', marker='*', linestyle=None, label='Ultimate\nStrength')
		# Curve Fit
		ax_plot(self.elasticStrain, np.polyval([self.elasticModulus,0], self.elasticStrain), linestyle='-.', color='gray', label='Elastic\nCurve Fit')
		ax.plot(100*np.log(1+self.plasticStrain), self.strengthCoefficient*np.log(1+self.plasticStrain)**self.strainHardeningExponent/1E+6, linestyle='--', color='gray', label='Hollomon\'s\nCurve Fit')
		# Layout
		ax.set_xlim([0, 1.45*np.amax(100*self.strain)])
		ax.set_ylim([0, 1.1*self.ultimateStrength/1E+6])
		ax.set_xlabel('Strain [%]')
		ax.set_ylabel('Stress [MPa]')
		ax.legend(loc='upper right')
		ax.set_title('Real Curve - ' + title)
		ax.grid(which='major', axis='x', linestyle='--', color='gray', alpha=0.75)
		ax.grid(which='minor', axis='x', linestyle='--', color='gray', alpha=0.50)
		ax.grid(which='major', axis='y', linestyle='--', color='gray', alpha=0.75)
		ax.grid(which='minor', axis='y', linestyle='--', color='gray', alpha=0.50)
		# Save
		fig.tight_layout()
		fig.savefig(fileName)
		plt.close(fig)
		return