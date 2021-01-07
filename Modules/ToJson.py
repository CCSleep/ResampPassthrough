import codecs

def _UstParser(Line):
	"""Barebone for Ust Command"""
	if Line.startswith("[#") and Line.endswith("]"):
		Data = Line[2:-1].lower()
		if Data != "trackend":
			return {"type":"header","data":Data}
		else:
			return {"type":"eof","data":None}
	else:
		KeyValuePair = Line.split("=")
		if len(KeyValuePair) == 1:
			return {"type":"string","data":KeyValuePair[0]}
		ValueList = KeyValuePair[1].split(",")
		if len(ValueList) == 1:
			return {"type":"keyValue","data":{KeyValuePair[0]:KeyValuePair[1]}}
		else:
			return {"type":"keyValue","data":{KeyValuePair[0]:ValueList}}

def Ust(File, codec="shift_jis"):
	"""Utility for converting UTAU Sequence Text to JSON"""
	EndData = {}
	_header = ""
	ReadFile = codecs.open(File, "r", codec)
	for line in ReadFile:
		line = line.rstrip('\r\n')
		#print(EndData)
		_parsed = _UstParser(line)
		if _parsed["type"] == "eof":
			return EndData
		elif _parsed["type"] == "header":
			_header = _parsed["data"]
			EndData[_header] = {}
		elif _parsed["type"] == "keyValue":
			EndData[_header] = {**EndData[_header], **_parsed["data"]}
		elif _parsed["type"] == "string":
			EndData[_header] = _parsed["data"]

def Oto(File, codec="shift_jis"):
	EndData = {}
	_header = ""
	ReadFile = codecs.open(File, "r", codec)
	for line in ReadFile:
		line = line.rstrip("\r\n").split('=', maxsplit=1)
		line[1] = line[1].split(",")
		EndData[line[1][0]] = {
		"File":line[0],
		"Alias":line[1][0],
		"Offset":line[1][1],
		"Consonant":line[1][2],
		"Cutoff":line[1][3],
		"PreUtterance":line[1][4],
		"Overlap":line[1][5]
		} # PascalCase to retain compatibility with UTAU
	return EndData
	
if __name__ == '__main__':
	print(Oto("../Voice/Roos/V/oto.ini"))