import re
from heredoc import HeredocStream

def parse(stream, out):
	for line in stream:
		if re.match('#.*', line):
			# Ignore comment.
			continue
		match = re.match('@parser (\w+)$', line)
		if match:
			parser_name = match.group(1)
			globals()[parser_name](stream, out)
			continue
		match = re.match('@parser (\w+) until (.+)$', line)
		if match:
			parser_name = match.group(1)
			delimiter = match.group(2)
			heredoc = HeredocStream(stream, delimiter)
			globals()[parser_name](heredoc, out)
			continue
		# Pass everything else through verbatim.
		out.writelines(line)

# Sample alternative parser.
def block_quoter(stream, out):
	for line in stream:
		if line == '<\n':
			return
		else:
			out.writelines("> " + line)

def dumb_block_quoter(stream, out):
	for line in stream:
		out.writelines("> " + line)

def markdown(stream, out):
	md_source = ''.join(stream.readlines())
	import markdown
	html = markdown.markdown(md_source)
	out.write(html)
