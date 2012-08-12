class HeredocStream:
	def __init__(self, stream, delimiter):
		self.stream = stream
		self.delimiter = delimiter
	
	def __iter__(self):
		for line in self.stream:
			if line == self.delimiter + '\n':
				raise StopIteration
			else:
				yield line
