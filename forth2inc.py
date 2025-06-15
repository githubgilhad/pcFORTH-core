#!/usr/bin/python -u
# vim: fileencoding=utf-8:nomodified:nowrap:textwidth=0:foldmethod=marker:foldcolumn=4:ruler:showcmd:lcs=tab\:|- list:tabstop=8:noexpandtab:nosmarttab:softtabstop=0:shiftwidth=0


import argparse
import re
import sys

# global
known = {}
glob_imm = False
fout=0
glob_middle=""
glob_stat=0
depth=0
lineno=0
direct_read=False
parser=None

def parse_args():
	global parser
	parser = argparse.ArgumentParser(description="Translate FORTH definitions to assembler code.")
	parser.add_argument("-s","--source", nargs="?", help="source file to translate (words.4int)")
	parser.add_argument("-o", "--outfile", nargs="?", help="output file to create (words.inc)" )
	parser.add_argument("-t", "--translatefile", nargs="*", help="file with name pairs ( forth C )" )
	parser.add_argument("asmfiles", nargs="*", help="One or more assembler files with known words (asm.S asm1.S asm2.S ...)")
	parser.add_argument("-v", "--verbose", action="store_true")
	parser.add_argument("-e", "--export", nargs="?", help="exports name pairs to this file (eg. translate.txt)")
	parser.add_argument("-c", "--col", type=int, default=40, help="Column for comments (default: 40)")
	return parser.parse_args()

def load_translations(asmfile):
	global known
	patternTXT = re.compile(r'^\s*([^\s]*)\s*([^\s]*)\s*')
	try:
		with open(asmfile, encoding='utf-8') as f:
			for line in f:
				m = patternTXT.search(line)
				if m:
					name, label = m.groups()
					known[name] = label
	except FileNotFoundError:
		print(f"FileNotFoundError {asmfile} - ignoring")

def load_known_words(asmfile):
	global known
	patternDW = re.compile(r'^\s*DEFWORD\s+"?(\w+)"?,[^,]*,\s*"([^"]+)",')
	patternDV = re.compile(r'^\s*DEFVAR\s+"?(\w+)"?')
	patternDC = re.compile(r'^\s*DEFCONST\s+"?(\w+)"?')
	patternDC1 = re.compile(r'^\s*DEFCONST1\s+"?(\w+)"?,')
	patternDC2 = re.compile(r'^\s*DEFCONST2\s+"?(\w+)"?,')
	patternPORT = re.compile(r'^\s*PORT\s+(\w+),')
	try:
		with open(asmfile, encoding='utf-8') as f:
			for line in f:
				m = patternDW.search(line)
				if m:
					label, name = m.groups()
					if not '\\' in name:
						known[name] = label
				m = patternDV.search(line)
				if m:
					name, = m.groups()
					known[name] = "var_"+name
				m = patternDC.search(line)
				if m:
					name, = m.groups()
					known[name] = "const_"+name
				m = patternDC1.search(line)
				if m:
					name, = m.groups()
					known[name] = "const_"+name
				m = patternDC2.search(line)
				if m:
					name, = m.groups()
					if not '\\' in name:
						known[name] = "const_"+name
				m = patternPORT.search(line)
				if m:
					name, = m.groups()
					for base in ("PORT","PIN","DDR"):
						known[base+name] = "const_"+base+name
	except FileNotFoundError:
		print(f"FileNotFoundError {asmfile} - ignoring")

def strip_forth_comments(line,nest=0):
	result = ''
	i = 0
	while i < len(line):
		if line[i] == '\\':
			break
		elif line[i] == '(':
			nest += 1
			i += 1
			while i < len(line) and nest > 0:
				if line[i] == '(':
					nest += 1
				elif line[i] == ')':
					nest -= 1
				i += 1
		else:
			result += line[i]
			i += 1
	return (nest,result.strip())

def extract_nick_from_comment(line):
	m = re.search(r'\(.+"([^"]+)".+\)', line)
	return m.group(1) if m else None
def extract_immediate_from_line(line):
	global glob_imm
	m = re.search(r'\sIMMEDIATE\s', line)
	if m:
		glob_imm = True
	return "FLG_IMMEDIATE" if m else "0"

def out( left, right):
	global args,fout,glob_middle
	tab = 0
	if len(left):
		if left[0]=='\t':
			tab = -7
	if (len(left) or len(right)):
		fout.write(f"{left:<{args.col+tab}}")
		if len(right):
			fout.write(f" {glob_middle}{right}\n")
		else:
			fout.write("\n")

def ToAscii(s):
	return s.replace('\\', '\\\\').replace('"', '\\"')
def do_token(token,left,right,line):
	global glob_stat, glob_imm, known, fout, lineno, direct_read
#	token.replace('\\(','(')
#	print(f"{lineno}: [{token}] [{line}]")
	direct_read=False
	if (glob_stat == 0) and (token==':'):
		glob_stat=1
		direct_read=True
		return (left,right)
	if len(left):
		out(left, right)
		left=""
		right=""
	if (glob_stat == 0):
		print(f"COMMAND {token} in line [{line}] at {lineno} !!!")
		return(left,right)
	if (glob_stat == 1):
#		nick = extract_nick_from_comment(line)
		nick = None
		imm = extract_immediate_from_line(line)
		if not nick:
			if  token in known:
				nick=known[token]
			else:
				nick = "w_"+token
		else:
			nick = "w_"+nick
		fout.write("\n")
		left=f'DEFWORD {nick},{imm},"{ToAscii(token)}",f_docol'
		if token in known:
			if known[token]!=nick:
				print(f"redefining known[{token}]={known[token]} to {nick} at {lineno}")
		known[token]=nick
		out(left, right)
		left=""
		right=""
		glob_stat=2
		return (left,right)
	if (glob_stat==2):
		if token==';':
			left='	.long w_exit_cw'
			out(left, right)
			left=""
			right=""
			glob_stat=0
			glob_imm=False
			return (left,right)
		else:
			if token=="IMMEDIATE":
				glob_imm=False
				return (left,right)
			nick=known.get(token)
			if nick:
				left=f'	.long {nick}_cw'
			else:
				left=f'	.long w_lit2_cw, {token}'
				if args.verbose:
					ok=False
					try:
						int(token,0)
						ok=True
					except ValueError:
						pass
					if not ok and (token[:2] != "\\'" and token[:2] != "\\\""):
						print(f"	unknown token {token} at {lineno}")
					
			out(left, right)
			left=""
			right=""
			return (left,right)
	print(f"*** WTF error  do_token([{token}],[{left}],[{right}],[{line}]) glob_stat={glob_stat} at {lineno}")

def process(line, depth, fout):
	global glob_middle, lineno, known
#	comm= "(" in known
	comm=True
	glob_middle=f"// {lineno:06} 	"
	right=line
	left=""
	
#	code,depth = strip_forth_comments(line,depth)
	code=line
	code=code.strip()
	i=0
	while (i<len(code)):
		if (not direct_read) and (depth or (comm and (code[i:i+2] == '( '))):
			if code[i:i+2] == '( ':
				depth +=1
				i+=2
			while i < len(code) and depth > 0:
				if code[i:i+2] == '( ':
					depth += 1
				elif code[i] == ')':
					depth -= 1
				i += 1
			continue
		if code[i:i+2] == "\\'":	# special: insert next token as is
			i+=2
			start = i
			while i < len(code) and not code[i].isspace():
				i += 1
			left=f"	.long {code[start:i]}"
			out(left, right)
			left = ""
			right = ""
			continue
		if code[i:i+2] == "\\\"":	# special: insert next token as ascii
			i+=2
			start = i
			while i < len(code) and not code[i]=="\"":
				i += 1
			left=f"	.ascii \"{ToAscii(code[start:i])}\""
			i += 1
			out(left, right)
			left = ""
			right = ""
			continue
		if code[i:i+2] == '\\ ':
			break
		if code[i:i+2] == '\\\t':
			break
		if code[i].isspace():
			i += 1
			continue
#		if code[i:i+3] == '." ':
#			i += 3
#			start = i
#			while i < len(code) and code[i] != '"':
#				i += 1
#			left=f'	.byte {i-start}'
#			out(left, right)
#			right=""
#			left=f'	.asciiz "{code[start:i]}"'
#			out(left, right)
#			left=""
#			i += 1
#			continue
		else:
#			if code[i] == '\\':
#				i += 1
			start = i
			while i < len(code) and not code[i].isspace():
				i += 1
			(left,right)=do_token(code[start:i], left,right,line)
			continue
	if (len(left) or len(right)):
		out(left, right)
	return depth

def main():
	global args,depth,fout,known,lineno
	args = parse_args()
	for asmfile in args.asmfiles:
		if args.verbose:
			print( f"Importing {asmfile}")
		load_known_words(asmfile)	# add to known
		if args.verbose:
			print( f"known words so far: {len(known)}")
	if args.translatefile:
		for tr in args.translatefile:
			if args.verbose:
				print(f"translatefile: {tr}")
			load_translations(tr)
			if args.verbose:
				print( f"known words so far: {len(known)}")

	if args.verbose:
		print( f"Processing: {args.source} -> {args.outfile}")
	if args.source:
		with open(args.source, encoding='utf-8') as f:
			source_lines = f.readlines()
			with  open(args.outfile, 'w',  encoding='utf-8') as fout:
				fout.write(";/* vim: set filetype=asm noexpandtab fileencoding=utf-8 nomodified nowrap textwidth=270 foldmethod=marker foldmarker={{{,}}} foldcolumn=4 ruler showcmd lcs=tab\\:|- list: */\n\n")
				for a_lineno, line in enumerate(source_lines):
					lineno = a_lineno+1
					depth = process(line.rstrip('\n'), depth, fout);
	if args.verbose:
		print( f"known words so far: {len(known)}")
	if args.export:
		with  open(args.export, 'w',  encoding='utf-8') as fout:
			for n,v in sorted(known.items()):
				fout.write(f"{n:<16}	{v}\n")
		print(f"name -> nick pairs exported to: {args.export}")
	if not ( args.source or args.asmfiles ):
		parser.print_help()


if __name__ == "__main__":
	main()
