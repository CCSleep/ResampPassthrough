from Modules.Pitch.Factory import MainFactory
from Modules.ToJson import Oto 
from audiolazy.lazy_midi import midi2str
import utaupy
import string
import random
import math
import os, subprocess, shutil

def RandomString(Length):
	Letters = string.ascii_lowercase
	return ''.join(random.choice(Letters) for i in range(Length))

UST_FILE = "filet.ust"
OTO_FILE = "Voice\\NanaMio\\oto.ini"
VB_PATH = "Voice\\NanaMio"
RESAMPLER_PATH = "Resampler\\macres.exe"
WAVTOOL_PATH = "Resampler\\wavtool-yawu.exe"
CACHE_PATH = "Cache\\"
OUTPUT_FILE = "temp.wav"
UstObject = utaupy.ust.load(UST_FILE)
OtoObject = Oto(OTO_FILE)
UstParts = UstObject.notes[4:28]

shutil.rmtree(os.path.join(os.getcwd(), CACHE_PATH))
os.mkdir(os.path.join(os.getcwd(), CACHE_PATH))

PreviousNote = -1
PreviousLength = 0
Tempo = round(float(UstObject.tempo))
MSPassed = 0
open(OUTPUT_FILE, "w+")
for NIndex, Note in enumerate(UstParts):
	print("prevnote", PreviousNote)
	Rest = False
	if Note.lyric in OtoObject.keys():
		LocalOto = OtoObject[Note.lyric]
	else:
		LocalOto = None
		Rest = True

	Lyric = Note.lyric
	Length = Note.length
	NoteNum = Note.notenum
	PreUtterance = float(LocalOto["PreUtterance"]) if not Rest else 0
	Velocity = Note.velocity

	# try:
	# 	PreUtterance = Note.get_by_key("PreUtterance")
	# except KeyError:
	# 	PreUtterance = 0

	try:
		StartPoint = Note.get_by_key("StartPoint")
	except KeyError:
		StartPoint = 0

	try:
		PBS = Note.pbs
	except KeyError:
		PBS = None
	
	try:
		PBW = Note["PBW"].split(",")
	except KeyError:
		PBW = None

	try:
		PBY = Note["PBY"].split(",")
		for Index, Var in enumerate(PBY):
			if Var == "":
				PBY[Index] = "0"
	except KeyError:
		PBY = []

	try:
		PBM = Note.pbm
	except KeyError:
		PBM = []

	try:
		VBR = Note.get_by_key("VBR").split(",")
	except KeyError:
		VBR = None

	try:
		Flags = Note.get_by_key("Flags")
	except KeyError:
		Flags = "?"

	try:
		Modulation = Note.get_by_key("Modulation")
	except KeyError:
		Modulation = 100

	try:
		Intensity = Note.get_by_key("Intensity")
	except KeyError:
		Intensity = 100

	try:
		StartPoint = Note.get_by_key("StartPoint")
	except KeyError:
		StartPoint = 0

	try:
		Envelope = Note.get_by_key("Envelope")
		Envelope = Envelope.replace("%", LocalOto["Overlap"]).split(",")
	except (KeyError, TypeError):
		Envelope = ["0","5","35","0","100","100","0"]

	FileOrder = f"{NIndex:05}"
	if Rest:
		# Parameters = [os.path.join(os.getcwd(), RESAMPLER_PATH),os.path.join(os.getcwd(), CACHE_PATH, SILENCE_FILE), os.path.join(os.getcwd(),f"{FileOrder}_Blank_{RandomString(6)}.wav"),utaupy.ust.notenum_as_abc(NoteNum),"100","?","0",str(int(Length//50 *50 if Length/50 - Length//50 < 0.5 else math.ceil(Length/50) * 50)),"0","0","100","0"]
		# Segment = AudioSegment.silent(duration=Length)
		WavtoolParam = [
			os.path.join(os.getcwd(), WAVTOOL_PATH), 
			os.path.join(os.getcwd(), OUTPUT_FILE), 
			OutputFile, 
			str(MSPassed), 
			str(Length)
		] + (["0"] * 11)
		PreviousNote = -1
		MSPassed += float(Length)
		subprocess.call(WavtoolParam)
	else:
		if PreviousNote == -1:
			PrevNote = NoteNum
		else:
			PrevNote = int(PreviousNote)

		if PBS is not None and PBW is not None:
			PB = MainFactory()
			PB.AddPitchBends(MSPassed, MSPassed + float(Length), PBS, PBW, PrevNoteNum=PrevNote, CurrentNoteNum=NoteNum, PBY=PBY, PBM=PBM, VBR=VBR)
			PitchBendData = PB.RenderPitchBends(int(math.ceil((MSPassed + PBS[0]) / 5)), int(math.floor((MSPassed + float(Length)) / 5)), NoteNum)
		else:
			PitchBendData = None


		# Bite Correction (The previous note should last for half the length before overlap)
		if PreUtterance - float(LocalOto["Overlap"]) > (PreviousLength // 2):
			CorrectionRate = (PreviousLength // 2) /  (PreUtterance - float(LocalOto["Overlap"]))
			BitedPreUtterance = PreUtterance * CorrectionRate
			BitedOverlap = float(LocalOto["Overlap"]) * CorrectionRate
		else:
			BitedPreUtterance = PreUtterance
			BitedOverlap = float(LocalOto["Overlap"])

		BitedSTP = PreUtterance - BitedPreUtterance  

		LengthRequire = Length + float(StartPoint) - BitedSTP + BitedOverlap + 50
		if LengthRequire < float(LocalOto["Consonant"]):
			LengthRequire = float(LocalOto["Consonant"])

		LengthRequire = LengthRequire//50 *50 if LengthRequire/50 - LengthRequire//50 < 0.5 else math.ceil(LengthRequire/50) * 50

		InputFile = os.path.join(os.getcwd(), VB_PATH, LocalOto["File"])
		OutputFile = os.path.join(os.getcwd(), CACHE_PATH, f"{FileOrder}_{Lyric}_{RandomString(6)}.wav")

		Parameters = [
			os.path.join(os.getcwd(), RESAMPLER_PATH),
			InputFile, 
			OutputFile,
			midi2str(NoteNum),
			str(Velocity),
			Flags,
			LocalOto["Offset"],
			str(int(LengthRequire)),
			LocalOto["Consonant"],
			LocalOto["Cutoff"],
			Intensity,
			Modulation,
			f"!{Tempo}" if PitchBendData is not None else "",
			f"{PitchBendData}" if PitchBendData is not None else ""
		]

		print(Parameters)

		PreviousNote = NoteNum
		PreviousLength = float(Length)
		MSPassed += float(Length)
		subprocess.call(Parameters)

		if NIndex + 1 < len(UstParts) and UstParts[NIndex+1].lyric in OtoObject.keys():
			NextOto = OtoObject[UstParts[NIndex+1].lyric]
			NextPreUtterance = float(NextOto["PreUtterance"])
			NextOverlap = float(NextOto["Overlap"])

			WavtoolCorrection = PreUtterance - NextPreUtterance + NextOverlap
		else:
			WavtoolCorrection = PreUtterance

		sign = "+" if WavtoolCorrection >= 0 else ""
		WavtoolParam = [
			os.path.join(os.getcwd(), WAVTOOL_PATH), 
			os.path.join(os.getcwd(), OUTPUT_FILE), 
			OutputFile, 
			str(float(StartPoint)), 
			f"{Length}@{float(Tempo)}{sign}{WavtoolCorrection}"
		] + [str(i) for i in Envelope] 

		subprocess.call(WavtoolParam)


