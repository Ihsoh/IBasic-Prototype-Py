#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import core

funcs = {}

def _check_args(fname, args_count, args, types):
	if len(args) < args_count:
		raise Exception("Function(%s) too few arguments" % fname)
	elif len(args) > args_count:
		raise Exception("Function(%s) too many arguments" % fname)
	for i in range(len(args)):
		if not isinstance(args[i], types[i]):
			raise Exception("Function(%s) argument(%d) type is error" % (fname, i))

def _check_vargs(fname, args, t):
	for i in range(len(args)):
		if not isinstance(args[i], t):
			raise Exception("Function(%s) argument(%d) type is error" % (fname, i))

def _check_args_mt(fname, args_count, args, types):
	if len(args) < args_count:
		raise Exception("Function(%s) too few arguments" % fname)
	elif len(args) > args_count:
		raise Exception("Function(%s) too many arguments" % fname)
	for i in range(len(args)):
		match_type = False
		for t in types[i]:
			if isinstance(args[i], t):
				match_type = True
				break
		if not match_type:
			raise Exception("Function(%s) argument(%d) type is error" % (fname, i))

def func_input(args):
	_check_args("input", 0, args, ())
	return str(input())

def func_print(args):
	for item in args:
		sys.stdout.write(unicode(item))
		sys.stdout.flush()
	return None

def func_sum(args):
	_check_vargs("sum", args, float)
	total = 0.0
	for item in args:
		total = total + float(item)
	return total

def func_str(args):
	if(len(args) != 1):
		raise Exception("Invalid str")
	return str(args[0])

def func_float(args):
	if(len(args) != 1):
		raise Exception("Invalid float")
	return float(args[0])

def init():
	funcs["Input"] = func_input
	funcs["Print"] = func_print
	funcs["Sum"] = func_sum
	funcs["Str"] = func_str
	funcs["Float"] = func_float

def get_func(name):
	if name in funcs.keys():
		return funcs[name]
	else:
		return None
