from baseconv import BaseConverter
import string
import re

class Ub64:
	"""Classes for converting Base64 for UTAU (runs number A-Za-z0-9+/)"""
	
	@staticmethod
	def encode(number):
		b64 = BaseConverter(string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/")
		if number < 0:
			number += 4096
		number = max([0, min([4095, number])])
		result = b64.encode(number)
		if len(result) < 2:
			result = "A"+result
		return result

	@staticmethod
	def decode(number):
		b64 = BaseConverter(string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/")
		result = int(b64.decode(number))
		if result > 2047:
			result -= 4096
		return result

if __name__ == '__main__':
	s = "9T9U9V9X9Z9b9f9j9p9v93+B+M+Y+l+x++/K/U/d/l/r/w/0/3/5/7/8/9/+////AA"
	j = []
	while len(s) > 0:
		j.append(Ub64.decode(s[0:2]))
		s = s[2:]

	print(j)