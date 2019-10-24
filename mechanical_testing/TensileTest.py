import numpy as np
import pandas as pd
import copy

class TensileTest:
	def __init__(self, file, length, diameter):
		self._readFromFile(file)
		self._defineDimensions(length, diameter)
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
		self.area = np.pi * diameter**2 / 4
		return