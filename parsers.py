import os
import sys
import re
import base64
from heredoc import HeredocStream

def parse(parent, stream, out, args):
	for line in stream:
		if re.match('#.*', line):
			# Ignore comment.
			continue
		match = re.match('@parser (\w+)$', line)
		if match:
			parser_name = match.group(1)
			globals()[parser_name](parse, stream, out, args)
			continue
		match = re.match('@parser (\w+) until (.+)$', line)
		if match:
			parser_name = match.group(1)
			delimiter = match.group(2)
			heredoc = HeredocStream(stream, delimiter)
			globals()[parser_name](parse, heredoc, out, args)
			continue
		match = re.match('@{', line)
		if match:
			# Execute block of user code.
			heredoc = HeredocStream(stream, '}')
			python_block(parse, heredoc, out, args)
			continue
		# Pass everything else through verbatim.
		out.writelines(line)

# Sample alternative parser.
def block_quoter(parent, stream, out, args):
	for line in stream:
		if line == '<\n':
			return
		else:
			out.writelines("> " + line)

def dumb_block_quoter(parent, stream, out, args):
	for line in stream:
		out.writelines("> " + line)

def markdown(parent, stream, out, args):
	md_source = ''.join(stream.readlines())
	import markdown
	html = markdown.markdown(md_source, output_format='html5')
	out.write(html)

def html_doc(parent, stream, out, args):
	out.writelines('<!DOCTYPE html><html><body>\n')
	parent(html_doc, stream, out, args)
	out.writelines('</body></html>\n')

def duck_hunter(parent, stream, out, args):
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
	parent(duck_hunter, duck_hunter_stream(), out, args)

def duck_breeder(parent, stream, out, args):
	def duck_breeder_filter():
		for line in stream:
			yield line.replace('{duckling}', '{duck}')
	parent(duck_breeder, duck_breeder_filter(), out, args)

def htmlify_inline_code(parent, stream, out, args):
	def htmlify_inline_code_stream():
		for line in stream:
			yield re.sub('`(.+?)\'', '<tt>\\1</tt>', line)
	parent(htmlify_inline_code, htmlify_inline_code_stream(), out, args)

def python_block(parent, stream, out, args):
	python_source = ''.join(stream.readlines())
	try:
		ast = compile(python_source, '<string>', 'exec')
		exec(ast)
	except:
		out.writelines('Error in Python block:\n')
		out.writelines(str(sys.exc_info()[0]))

def image_embed(parent, stream, out, args):
	def image_embed_filter():
		for line in stream:
			m = re.search('{img:(.*?)}', line)
			if m is None:
				yield line
			else:
				imgdir = os.getcwd() if args.source == '-' else os.path.dirname(args.source)
				imgfn = m.group(1)
				img = os.path.join(imgdir, imgfn)
				extn = os.path.splitext(img)[1].replace('.','')
				b64data = base64.b64encode(open(img).read())
				out.writelines('<img src="data:image/%s;base64,%s" alt="%s" />' % (extn, b64data, imgfn))
	parent(image_embed, image_embed_filter(), out, args)
