#!/usr/bin/python
# -*- coding: utf-8 -*-

class LexerException(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class Lexer(object):
	def __init__(self, code):
		if isinstance(code, str) or isinstance(code, unicode):
			self.__tokens = self.__lexer(code)
		elif isinstance(code, list):
			self.__tokens = code
		else:
			raise LexerException("Invalid code type")
		self.__index = 0

	def __lexer(self, code):
		tokens = []
		token = ""
		i = 0
		while i < len(code):
			char = code[i]
			if char == " " 	\
				or char == "\t"	\
				or char == "\r"	\
				or char == "\f"	\
				or char == "\v":
				if token != "":
					tokens.append(token)
					token = ""
			elif char == "\n":
				if token != "":
					tokens.append(token)
					token = ""
				tokens.append("\n")
			elif char == "\"":
				if token != "":
					tokens.append(token)
				token = "\""
				i = i + 1
				while True:
					char = code[i]
					if char == "\"":
						token = token + char
						break
					else:
						token = token + char
					i = i + 1
					if i == len(code):
						raise LexerException("Expect '\"'")
			elif char == "+" or char == "-"	\
					or char == "*" or char == "/"	\
					or char == "(" or char == ")"	\
					or char == "^" or char == "="	\
					or char == ",":
				if token != "":
					tokens.append(token)
					token = ""
				tokens.append(char)
			elif char == "<":
				if token != "":
					tokens.append(token)
					token = ""
				if i + 1 == len(code):
					tokens.append("<")
				else:
					if code[i + 1] == ">" or code[i + 1] == "=":
						i = i + 1
						tokens.append("<" + code[i])
					else:
						tokens.append("<")
			elif char == ">":
				if token != "":
					tokens.append(token)
					token = ""
				if i + 1 == len(code):
					tokens.append(">")
				else:
					if code[i + 1] == "=":
						i = i + 1
						tokens.append(">=")
					else:
						tokens.append(">")
			elif (char >= "A" and char <= "Z")	\
					or (char >= "a" and char <= "z")	\
					or (char >= "0" and char <= "9")	\
					or char == "_" or char == ".":
				token = token + char
			i = i + 1
		if token != "":
			tokens.append(token)
		return tokens

	def get_tokens(self):
		return self.__tokens

	def next(self):
		self.__index = self.__index + 1
		if self.__index - 1 >= len(self.__tokens):
			return None
		else:
			return self.__tokens[self.__index - 1]

	def prev(self):
		self.__index = self.__index - 1
		if self.__index + 1 < 0 or self.__index + 1 >= len(self.__tokens):
			return None
		else:
			return self.__tokens[self.__index + 1]

	def get_token(self):
		if self.__index >= len(self.__tokens):
			return None
		else:
			return self.__tokens[self.__index]
