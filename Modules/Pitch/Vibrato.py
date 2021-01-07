import math

class Vibrato:
	def __init__(self, startMS, endMS, cycleMS, amplitude, phaseIn, phaseOut, phasePercent, pitchChange, baseFreqSlope):
		self.startMS = startMS
		self.endMS = endMS
		lengthMS = endMS - startMS
		self.phaseIn = phaseIn / 100.0 * lengthMS
		self.phaseOut = phaseOut / 100.0 * lengthMS
		self.amplitude = amplitude / 10.0
		self.baseFreq = 2 * math.pi / cycleMS
		self.phase = 2 * math.pi * (phasePercent / 100.0)
		self.pitchChange = pitchChange / (math.exp(1) * 1000) # decicents

		self.startFreq = self.baseFreq * (-1 * baseFreqSlope / 800 + 1)
		endFreq = self.baseFreq * (baseFreqSlope / 800 + 1)
		if lengthMS == 0:
			self.freqSlope = 0
		else:
			self.freqSlope = (endFreq - self.startFreq) / lengthMS

	def Apply(self, positionMS):
		frequency = self.startFreq + self.freqSlope * (positionMS - self.startMS)
		if positionMS < self.startMS:
			return 0
		elif positionMS < self.startMS + self.phaseIn:
			incScale = abs(positionMS - self.startMS) / self.phaseIn
			return (self.amplitude * incScale * math.sin((positionMS - self.startMS) * frequency - self.phase) + (self.pitchChange * incScale))
		elif positionMS < self.endMS - self.phaseOut:
			return (self.amplitude * math.sin((positionMS - self.startMS) * frequency - self.phase) + self.pitchChange)
		elif positionMS < self.endMS:
			decScale = abs(self.endMS - positionMS) / self.phaseOut
			return (self.amplitude * decScale * math.sin((positionMS - self.startMS) * frequency - self.phase) + (self.pitchChange * decScale))
		else:
			return 0

if __name__ == "__main__":
	v = Vibrato(0,600,100,40,0,0,0,0,0)
	j = []
	for i in range(601):
		j.append(v.Apply(i))

	print(j)