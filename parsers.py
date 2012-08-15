import re
from heredoc import HeredocStream

def parse(parent, stream, out):
	for line in stream:
		if re.match('#.*', line):
			# Ignore comment.
			continue
		match = re.match('@parser (\w+)$', line)
		if match:
			parser_name = match.group(1)
			globals()[parser_name](parse, stream, out)
			continue
		match = re.match('@parser (\w+) until (.+)$', line)
		if match:
			parser_name = match.group(1)
			delimiter = match.group(2)
			heredoc = HeredocStream(stream, delimiter)
			globals()[parser_name](parse, heredoc, out)
			continue
		# Pass everything else through verbatim.
		out.writelines(line)

# Sample alternative parser.
def block_quoter(parent, stream, out):
	for line in stream:
		if line == '<\n':
			return
		else:
			out.writelines("> " + line)

def dumb_block_quoter(parent, stream, out):
	for line in stream:
		out.writelines("> " + line)

def markdown(parent, stream, out):
	md_source = ''.join(stream.readlines())
	import markdown
	html = markdown.markdown(md_source, output_format='html5')
	out.write(html)

def html_doc(parent, stream, out):
	out.writelines('<!DOCTYPE html><html><body>\n')
	parent(html_doc, stream, out)
	out.writelines('</body></html>\n')

def duck_hunter(parent, stream, out):
	def duck_hunter_stream():
		for line in stream:
			if line == '{duck}\n':
				yield """
					   _
					 >(o)__
					  (_~_/
					~~~~~~~~~
					"""[1:].replace('\t', '')
			else:
				yield line
	parent(duck_hunter, duck_hunter_stream(), out)

def duck_breeder(parent, stream, out):
	def duck_breeder_filter():
		for line in stream:
			yield line.replace('{duckling}', '{duck}')
	parent(duck_breeder, duck_breeder_filter(), out)

def htmlify_inline_code(parent, stream, out):
	def htmlify_inline_code_stream():
		for line in stream:
			yield re.sub('`(.+?)\'', '<tt>\\1</tt>', line)
	parent(htmlify_inline_code, htmlify_inline_code_stream(), out)
