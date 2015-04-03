#!/usr/bin/python
# -*- coding: utf-8 -*-

from lexer import Lexer
import re

class ParserException(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class ASTNodeFile(object):
	def __init__(self, function_list):
		self.function_list = function_list

class ASTNodeFunction(object):
	def __init__(self, fname, args, statements):
		self.fname = fname
		self.args = args
		self.statements = statements

class ASTNodeLet(object):
	def __init__(self, vname, expr):
		self.vname = vname
		self.expr = expr

class ASTNodeCall(object):
	def __init__(self, expr):
		self.expr = expr

class ASTNodeIf(object):
	def __init__(self, expr, statements0, statements1):
		self.expr = expr
		self.statements0 = statements0
		self.statements1 = statements1

class ASTNodeReturn(object):
	def __init__(self, expr):
		self.expr = expr

class ASTNodeExit(object):
	def __init__(self):
		pass

class ASTNodeDo(object):
	def __init__(self, statements):
		self.statements = statements

class ASTNodeEmptyLine(object):
	def __init__(self):
		pass

class Parser(object):
	def __init__(self, code):
		self.__lexer = Lexer(code)
		self.__function_list = []

	def __is_identifier(self, token):
		return re.match(r"^[A-Za-z_]{1}[A-Za-z0-9_]*$", token)

	def get_function(self, fname):
		for i in range(0, len(self.__function_list)):
			if self.__function_list[i].fname == fname:
				return self.__function_list[i]
		return None

	def __skip_lf(self):
		lex = self.__lexer
		while lex.get_token() == "\n":
			lex.next()

	def parse_function(self):
		lex = self.__lexer
		self.__skip_lf()
		if lex.get_token() == "FUNCTION":
			lex.next()
			if not self.__is_identifier(lex.get_token()):
				raise ParserException("Invalid function name(%s)" % lex.get_token())
			fname = lex.next()
			args = []
			statements = []
			if lex.next() != "(":
				raise ParserException("Expect '('")
			if lex.get_token() != ")":
				if self.__is_identifier(lex.get_token()):
					args.append(lex.next())
				else:
					raise ParserException("Invalid identifier(%s)" % lex.get_token())
				while lex.get_token() == ",":
					lex.next()
					if self.__is_identifier(lex.get_token()):
						args.append(lex.next())
					else:
						raise ParserException("Invalid identifier(%s)" % lex.get_token())
			if lex.next() != ")":
				raise ParserException("Expect ')'")
			if lex.next() != "\n":
				raise ParserException("Invalid end of line")
			while lex.get_token() != "END":
				stat = self.parse_stat()
				if stat == None:
					raise ParserException("Expect 'END'")
				statements.append(stat)
			if lex.next() != "END":
				raise ParserException("Expect 'END'")
			if lex.next() != "\n":
				raise ParserException("Invalid end of line")
			self.__function_list.append(ASTNodeFunction(fname, args, statements))
			return True
		else:
			return False

	def parse_let(self):
		lex = self.__lexer
		if lex.get_token() == "LET":
			lex.next()
			if self.__is_identifier(lex.get_token()):
				vname = lex.next()
			else:
				raise ParserException("Invalid identifier(%s)" % lex.get_token())
			if lex.next() != "=":
				raise ParserException("Expect '='")
			expr = []
			while lex.get_token() != "\n" and lex.get_token() != None:
				expr.append(lex.next())
			if lex.next() != "\n":
				raise ParserException("Invalid end of line")
			return ASTNodeLet(vname, expr)
		else:
			return None

	def parse_call(self):
		lex = self.__lexer
		if lex.get_token() == "CALL":
			lex.next()
			if not self.__is_identifier(lex.get_token()):
				raise ParserException("Invalid identifier(%s)" % lex.get_token())
			expr = []
			while lex.get_token() != "\n" and lex.get_token() != None:
				expr.append(lex.next())
			if lex.next() != "\n":
				raise ParserException("Invalid end of line")
			return ASTNodeCall(expr)
		else:
			return None

	def parse_if(self):
		lex = self.__lexer
		if lex.get_token() == "IF":
			lex.next()
			expr = []
			while lex.get_token() != "\n" and lex.get_token() != None and lex.get_token() != "THEN":
				expr.append(lex.next()) 
			if lex.next() != "THEN":
				raise ParserException("Expect 'THEN'")
			if lex.next() != "\n":
				raise ParserException("Invalid end of line")
			statements0 = []
			while lex.get_token() != "END" and lex.get_token() != "ELSE":
				stat = self.parse_stat()
				if stat == None:
					raise ParserException("Expect 'ELSE' or 'END'")
				statements0.append(stat)
			if lex.get_token() == "END":
				lex.next()
				if lex.next() != "\n":
					raise ParserException("Invalid end of line")
				return ASTNodeIf(expr, statements0, None)
			else:
				lex.next()
				if lex.next() != "\n":
					raise ParserException("Invalid end of line")
				statements1 = []
				while lex.get_token() != "END":
					stat = self.parse_stat()
					if stat == None:
						raise ParserException("Expect 'END'")
					statements1.append(stat)
				lex.next()
				if lex.next() != "\n":
					raise ParserException("Invalid end of line")
				return ASTNodeIf(expr, statements0, statements1)
		else:
			return None

	def parse_return(self):
		lex = self.__lexer
		if lex.get_token() == "RETURN":
			lex.next()
			expr = []
			while lex.get_token() != "\n" and lex.get_token() != None:
				expr.append(lex.next())
			if lex.next() != "\n":
				raise ParserException("Invalid end of line")
			return ASTNodeReturn(expr)
		else:
			return None

	def parse_exit(self):
		lex = self.__lexer
		if lex.get_token() == "EXIT":
			lex.next()
			if lex.next() != "\n":
				raise ParserException("Invalid end of line")
			return ASTNodeExit()
		else:
			return None

	def parse_do(self):
		lex = self.__lexer
		if lex.get_token() == "DO":
			lex.next()
			if lex.next() != "\n":
				raise ParserException("Invalid end of line")
			statements = []
			while lex.get_token() != "LOOP":
				stat = self.parse_stat()
				if stat == None:
					raise ParserException("Expect 'LOOP'")
				statements.append(stat)
			lex.next()
			if lex.next() != "\n":
				raise ParserException("Invalid end of line")
			return ASTNodeDo(statements)
		else:
			return None

	def parse_empty_line(self):
		lex = self.__lexer
		if lex.get_token() == "\n":
			lex.next()
			return ASTNodeEmptyLine()
		else:
			return None

	def parse_stat(self):
		lex = self.__lexer
		stat = self.parse_let()
		if stat != None:
			return stat
		stat = self.parse_call()
		if stat != None:
			return stat
		stat = self.parse_if()
		if stat != None:
			return stat
		stat = self.parse_return()
		if stat != None:
			return stat
		stat = self.parse_exit()
		if stat != None:
			return stat
		stat = self.parse_do()
		if stat != None:
			return stat
		stat = self.parse_empty_line()
		if stat != None:
			return stat
		if lex.get_token() != None:
			raise ParserException("Invalid keyword(%s)" % lex.get_token())
		return None 

	def parse(self):
		while self.parse_function():
			pass
