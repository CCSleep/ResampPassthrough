# Credit: github/titinko/utsu
# https://github.com/titinko/utsu/blob/master/src/main/java/com/utsusynth/utsu/model/song/pitch/portamento/

import math
import abc

class Portamento:
	__metaclass__  = abc.ABCMeta

	@abc.abstractmethod
	def GetStartPitch():
		"""Returns start pitch"""

	@abc.abstractmethod
	def GetEndPitch():
		"""Returns end pitch"""

class LinearPortamento(Portamento):
	"""Create Straight Line Portamento"""

	def __init__(self, x1, x2, y1, y2):
		self.x1 = x1
		self.x2 = x2
		self.y1 = y1
		self.y2 = y2
		self.slope = (y2 - y1) / (x2 - x1)

	def Apply(self, positionMS):
		if self.x2 < positionMS or positionMS < self.x1:
			print("Tried to apply a linear portamento that doesn't exist here.")
			return 0.0

		adjustedX = positionMS - self.x1
		return self.slope * adjustedX + self.y1

	def GetStartPitch(self):
		return self.y1

	def GetEndPitch(self):
		return self.y2

class QuadraticPortamento(Portamento):
	"""Create "j"-shaped Portamento"""
	def __init__(self, x1, x2, y1, y2):
		self.x1 = x1
		self.x2 = x2
		self.y1 = y1
		self.y2 = y2
		self.slope = (y2 - y1) / ((x2 - x1) ** 2)

	def Apply(self, positionMS):
		if self.x2 < positionMS or positionMS < self.x1:
			print("Tried to apply a quadratic portamento that doesn't exist here.")
			return 0.0

		adjustedX = positionMS - self.x1
		return self.slope * (adjustedX ** 2) + self.y1

	def GetStartPitch(self):
		return self.y1

	def GetEndPitch(self):
		return self.y2

class LogarithmicPortamento(Portamento):
	"""Create "r"-shaped Portamento"""
	def __init__(self, x1, x2, y1, y2):
		self.x1 = x1
		self.x2 = x2
		self.y1 = y1
		self.y2 = y2
		self.yStretch = (y2 - y1) / 6 # a as in aln(bx) + c
		self.xStretch = 20 / (x2 - x1) # b as in aln(bx) + c
		self.constant = (y2 - y1) / 2 # c as in aln(bx) + c

	def Apply(self, positionMS):
		y1 = self.y1
		y2 = self.y2
		if self.x2 < positionMS or positionMS < self.x1:
			print("Tried to apply a logaritmic portamento that doesn't exist here.")
			return 0.0

		adjustedX = positionMS - self.x1
		if adjustedX == 0.0:
			return y1

		pitch = (self.yStretch * math.log(adjustedX * self.xStretch)) + self.constant + y1
		if ((y2 > y1 and y1 > pitch) or (y2 < y1 and y1 < pitch)):
			return y1
		return pitch

	def GetStartPitch(self):
		return self.y1

	def GetEndPitch(self):
		return self.y2

class LogisticPortamento(Portamento):
	"""Create "s"-shaped Portamento"""
	def __init__(self, x1, x2, y1, y2):
		self.x1 = x1
		self.x2 = x2
		self.y1 = y1
		self.y2 = y2
		self.halfX = (x2 - x1) / 2 # x0 as in L / (1 + e^(-k * (x - x0)))
		self.steepness = 5 / self.halfX # k as in L / (1 + e^(-k * (x - x0)))
		self.maxY = (y2 - y1) # L as in L / (1 + e^(-k * (x - x0)))

	def Apply(self, positionMS):
		y1 = self.y1
		y2 = self.y2
		if self.x2 < positionMS or positionMS < self.x1:
			print("Tried to apply a logistic portamento that doesn't exist here.")
			return 0.0

		adjustedX = positionMS - self.x1

		return self.maxY / (1+ math.exp(-1 * self.steepness * (adjustedX - self.halfX))) + y1

	def GetStartPitch(self):
		return self.y1

	def GetEndPitch(self):
		return self.y2

if __name__ == '__main__':
	port = QuadraticPortamento(0,10,0,100)
	print(port.Apply(10))