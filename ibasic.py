#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import codecs

from parser import Parser
from core import *

def main():
	if len(sys.argv) != 2:
		print "ibasic.py {path}"
		return
	path = sys.argv[1]
	code = ""
	try:
		f = codecs.open(path, 'r', 'utf8')
		code = f.read()
		f.close()
	except:
		print "Cannot open ", path
		return
	cr = Core(code)

if __name__ == "__main__":
	main()
