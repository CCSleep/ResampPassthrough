import math
from .Utils import Ub64
from .Portamento import *
from .Vibrato import Vibrato

class PitchFactory:
	def __init__(self):
		self.portamento = {}
		self.vibrato = None

	def AddPortamento(self, NoteStartMS, PortamentoObj):
		if NoteStartMS in self.portamento:
			print("Error: tried to add portamento twice.")
		else:
			self.portamento[NoteStartMS] = PortamentoObj

	def RemovePortamento(self, NoteStartMS):
		self.portamento.pop(NoteStartMS)

	def AddVibrato(self, VibratoObj):
		if self.vibrato is not None:
			print("Error: tried to add overlapping vibrato.")
		else:
			self.vibrato = VibratoObj

	def RemoveVibrato(self):
		self.vibrato = None

	def IsEmpty(self):
		return len(self.portamento) == 0 and self.vibrato is None
	def GetMaxPortamento(self):
		if len(self.portamento) == 0:
			return None
		else:
			return self.portamento[max(list(self.portamento))]

	def Apply(self, positionMS):
		PortamentoVal = 0
		LastPortamento = self.GetMaxPortamento()
		if LastPortamento is not None:
			PortamentoVal = LastPortamento.Apply(positionMS)
		VibratoVal = 0
		if self.vibrato is not None:
			VibratoVal = self.vibrato.Apply(positionMS)
		return PortamentoVal + VibratoVal

class MainFactory:
	def __init__(self):
		self.pitchbends = {}

	def ShowPitchBends(self):
		print(self.pitchbends)
	
	def NextPitchStep(self, positionMS):
		return math.ceil(positionMS/5)

	def PrevPitchStep(self, positionMS):
		result = math.floor(positionMS/5)
		if result == self.NextPitchStep(positionMS):
			return result - 1
		return result

	def AddPitchBends(self, NoteStartMS, NoteLengthMS, PBS, PBW, PrevNoteNum, CurrentNoteNum, PBY=[], PBM=[], VBR=None):
		PBS = [float(i) for i in PBS]
		PBW = [float(i) for i in PBW]
		if len(PBS) == 1:
			PBS.append(0)

		StartMS = NoteStartMS + PBS[0]
		PitchStart = PrevNoteNum * 10 + PBS[1]
		

		if PBY is not []:
			PBY = [float(i) for i in PBY]

		for i in range(len(PBW)):
			EndMS = StartMS + PBW[i]
			PitchEnd = CurrentNoteNum * 10
			if len(PBW) > i + 1 and len(PBY) >= i + 1:
				PitchEnd += PBY[i]
			PitchShape = ""
			if len(PBM) >= i + 1:
				PitchShape = PBM[i]

			if PitchShape.lower() == "s":
				portamento = LinearPortamento(StartMS, EndMS, PitchStart, PitchEnd)
			elif PitchShape.lower() == "j":
				portamento = QuadraticPortamento(StartMS, EndMS, PitchStart, PitchEnd)
			elif PitchShape.lower() == "r":
				portamento = LogarithmicPortamento(StartMS, EndMS, PitchStart, PitchEnd)
			elif PitchShape == "":
				portamento = LogisticPortamento(StartMS, EndMS, PitchStart, PitchEnd)

			for i in range(self.NextPitchStep(StartMS), self.PrevPitchStep(EndMS) + 1):
				if i in list(self.pitchbends):
					self.pitchbends[i].AddPortamento(NoteStartMS, portamento)
				else:
					Object = PitchFactory()
					Object.AddPortamento(NoteStartMS, portamento)
					self.pitchbends[i] = Object

				StartMS = EndMS
				PitchStart = PitchEnd

		if VBR is not None:
			VBR = [float(i) for i in VBR]
			VibratoLengthMS = NoteLengthMS * (VBR[0] / 100)
			VibratoStartMS = NoteStartMS + NoteLengthMS - VibratoLengthMS
			VibratoEndMS = NoteStartMS + NoteLengthMS

			vibrato = Vibrato(
				VibratoStartMS,
				VibratoEndMS,
				VBR[1],
				VBR[2],
				VBR[3],
				VBR[4],
				VBR[5],
				VBR[6],
				0
				)

			for i in range(self.NextPitchStep(VibratoStartMS), self.PrevPitchStep(VibratoEndMS) + 1):
				# print(i)
				if i in list(self.pitchbends):
					self.pitchbends[i].AddVibrato(vibrato)
				else:
					Object = PitchFactory()
					Object.AddVibrato(vibrato)
					self.pitchbends[i] = Object

	def RemovePitchBends(NoteStartMS, NoteLengthMS, PBS, PBW, VBR):
		PBS = [float(i) for i in PBS]
		PBW = [float(i) for i in PBW]
		StartMS = NoteStartMS + PBS[0]
		EndMS = StartMS + sum(PBW)
		for i in range(self.NextPitchStep(StartMS), self.PrevPitchStep(EndMS) + 1):
			pitchbend = self.pitchbends[i]
			pitchbend.RemovePortamento(NoteStartMS)
			if pitchbend.IsEmpty():
				self.pitchbends.pop(i)

		if VBR[0] > 0 or VBR[1] > 0:
			NoteEndMS = NoteStartMS + NoteLengthMS
			for i in range(self.NextPitchStep(NoteStartMS), self.PrevPitchStep(NoteEndMS) + 1):
				pitchbend = self.pitchbends[i]
				pitchbend.Vibrato(NoteStartMS)
				if pitchbend.IsEmpty():
					self.pitchbends.pop(i)

	def RenderPitchBends(self, FirstStep, LastStep, NoteNum):
		result = ""
		NoteNumPitch = NoteNum * 10
		DefaultPitch = 0
		for i in range(FirstStep, LastStep+1):
			if i in list(self.pitchbends):
				portamento = self.pitchbends[i].GetMaxPortamento()
				if portamento is not None:
					DefaultPitch = portamento.GetStartPitch()
					break

		step = FirstStep
		while step <= LastStep:
			# print(step)
			if step in self.pitchbends:
				positionMS = step * 5
				RealPitch = self.pitchbends[step].Apply(positionMS)
				if self.pitchbends[step].GetMaxPortamento() is None:
					RealPitch += DefaultPitch

				diff = int((RealPitch - NoteNumPitch) * 10)
				result += Ub64.encode(diff)

				portamento = self.pitchbends[step].GetMaxPortamento()
				if portamento is not None:
					DefaultPitch = portamento.GetEndPitch()
			else:
				NumEmpty = 0
				EmptyStep = step
				while EmptyStep <= LastStep:
					if EmptyStep in self.pitchbends:
						break
					else:
						NumEmpty += 1
					EmptyStep += 1

				diff = int((DefaultPitch -  NoteNumPitch) * 10)
				result += Ub64.encode(diff)
				if NumEmpty > 1:
					result += f"#{NumEmpty - 1}#"

				step = EmptyStep - 1
			step += 1
		return result

if __name__ == '__main__':
	x = MainFactory()
	x.AddPitchBends(200,720,[-38],[74],61,68,VBR=[100,136.3,36.9,5,61.3,0,0,0])
	print(x.RenderPitchBends(0,720,68))