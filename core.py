#!/usr/bin/python
# -*- coding: utf-8 -*-

from lexer import *
from parser import *
import re
import funcs

class CoreException(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class ReturnException(Exception):
	def __init__(self, retvalue):
		Exception.__init__(self, "Invalid 'RETURN'")
		self.retvalue = retvalue

class ExitException(Exception):
	def __init__(self):
		Exception.__init__(self, "Invalid 'EXIT'")

class Expr(object):
	def __init__(self, code, var_list):
		funcs.init()
		self.__vars = var_list
		self.__lexer = Lexer(code)

	def get_var_value(self, name):
		if name in self.__vars.keys():
			return self.__vars[name]
		else:
			return None

	# Expression
	def stat_expr(self, cr):
		def atom():
			lex = self.__lexer
			result = None
			if lex.get_token() != None:
				if re.match(r"^[\+\-]{0,1}[0-9]+(\.[0-9]+){0,1}$", lex.get_token()):
					result = float(lex.next())
				elif lex.get_token()[0] == "\"":
					result = lex.get_token()[1:len(lex.next()) - 1]
				elif re.match(r"^[A-Za-z_]{1}[A-Za-z0-9_]*$", lex.get_token()):
					result = self.get_var_value(lex.get_token())
					#if result == None:
					#	raise CoreException("Undefined variable(%s)" % lex.get_token())
					lex.next()
				else:
					raise CoreException("Invalid expression(%s)" % lex.get_token())
			else:
				raise CoreException("Expect expression")
			return result
		def parentheses():
			lex = self.__lexer
			if lex.get_token() == "(":
				lex.next()
				result = expr()
				if lex.next() != ")":
					raise CoreException("Expect ')'")
				return result
			else:
				return atom()
		def call():
			lex = self.__lexer
			if re.match(r"^[A-Za-z_]{1}[A-Za-z0-9_]*$", lex.get_token()):
				func = funcs.get_func(lex.get_token())
				if func == None:
					func = cr.parser.get_function(lex.get_token())
				if func != None:
					lex.next()
					if lex.next() == "(":
						args = []
						if lex.get_token() != ")":
							args.append(expr())
							while lex.get_token() == ",":
								lex.next()
								args.append(expr())
							if lex.get_token() != ")":
								raise CoreException("Expect ')'")
						lex.next()
						if isinstance(func, ASTNodeFunction):
							return cr.run(func, args)
						else:
							return func(args)
					else:
						raise CoreException("Expect '('")
				else:
					return parentheses()
			else:
				return parentheses()
		def opt_unary():
			lex = self.__lexer
			result = None
			while lex.get_token() == "+" or lex.get_token() == "-":
				opt = lex.next()
				if opt == "+":
					result = expr()
				elif opt == "-":
					result = -expr()
			if result == None:
				result = call()
			return result
		def opt_pow():
			lex = self.__lexer
			result = opt_unary()
			while lex.get_token() == "^":
				lex.next()
				result = pow(result, opt_unary())
			return result
		def opt_mul_div_mod():
			lex = self.__lexer
			result = opt_pow()
			while lex.get_token() == "*" or lex.get_token() == "/" or lex.get_token() == "MOD":
				opt = lex.next()
				if opt == "*":
					result = result * opt_pow()
				elif opt == "/":
					result = result / opt_pow()
				elif opt == "MOD":
					result = result % opt_pow()
			return result
		def opt_add_sub():
			lex = self.__lexer
			result = opt_mul_div_mod()
			while lex.get_token() == "+" or lex.get_token() == "-":
				opt = lex.next()
				if opt == "+":
					result = result + opt_mul_div_mod()
				elif opt == "-":
					result = result - opt_mul_div_mod()
			return result
		def opt_comparison():
			lex = self.__lexer
			result = opt_add_sub()
			while lex.get_token() == "=" 	\
					or lex.get_token() == "<>"	\
					or lex.get_token() == "<"	\
					or lex.get_token() == "<="	\
					or lex.get_token() == ">"	\
					or lex.get_token() == ">=":
				opt = lex.next()
				if opt == "=":
					result = result == opt_add_sub()
				elif opt == "<>":
					result = result != opt_add_sub()
				elif opt == "<":
					result = result < opt_add_sub()
				elif opt == "<=":
					result = result <= opt_add_sub()
				elif opt == ">":
					result = result > opt_add_sub()
				elif opt == ">=":
					result = result >= opt_add_sub()
			return result
		def opt_logic():
			lex = self.__lexer
			result = opt_comparison()
			while lex.get_token() == "AND" or lex.get_token() == "OR":
				opt = lex.next()
				if opt == "AND":
					oprd = opt_comparison()
					result = result and oprd
				elif opt == "OR":
					oprd = opt_comparison()
					result = result or oprd
			return result
		def opt_not():
			lex = self.__lexer
			result = None
			while lex.get_token() == "NOT":
				lex.next()
				result = not expr()
			if result == None:
				result = opt_logic()
			return result
		def expr():
			return opt_not()
		return expr()

	def calc(self, cr):
		result = self.stat_expr(cr)
		if self.__lexer.get_token() != None:
			raise CoreException("Invalid expression")
		return result

class Core(object):
	def __init__(self, code):
		self.__parser = Parser(code)
		self.parser = self.__parser
		self.__parser.parse()
		self.run(self.__parser.get_function("Main"), [])

	def run_let(self, statement, var_list):
		if isinstance(statement, ASTNodeLet):
			expr = Expr(statement.expr, var_list)
			var_list[statement.vname] = expr.calc(self)
			return True
		else:
			return False

	def run_call(self, statement, var_list):
		if isinstance(statement, ASTNodeCall):
			expr = Expr(statement.expr, var_list)
			expr.calc(self)
			return True
		else:
			return False

	def run_if(self, statement, var_list):
		if isinstance(statement, ASTNodeIf):
			expr = Expr(statement.expr, var_list)
			result = expr.calc(self)
			if result:
				self.run_statements(statement.statements0, var_list)
			else:
				if statement.statements1 != None:
					self.run_statements(statement.statements1, var_list)
			return True
		else:
			return False

	def run_return(self, statement, var_list):
		if isinstance(statement, ASTNodeReturn):
			expr = Expr(statement.expr, var_list)
			raise ReturnException(expr.calc(self))
		else:
			return False

	def run_do(self, statement, var_list): 
		if isinstance(statement, ASTNodeDo):
			while True:
				try:
					self.run_statements(statement.statements, var_list)
				except ExitException, e:
					break
			return True
		else:
			return False

	def run_exit(self, statement, var_list):
		if isinstance(statement, ASTNodeExit):
			raise ExitException()
		else:
			return False

	def run_statement(self, statement, var_list):
		if self.run_let(statement, var_list):
			pass
		elif self.run_call(statement, var_list):
			pass
		elif self.run_if(statement, var_list):
			pass
		elif self.run_return(statement, var_list):
			pass
		elif self.run_do(statement, var_list):
			pass
		elif self.run_exit(statement, var_list):
			pass

	def run_statements(self, statements, var_list):
		ptr = 0
		while ptr < len(statements):
			statement = statements[ptr]
			self.run_statement(statement, var_list)
			ptr = ptr + 1

	def run(self, function, args):
		local_var_list = {}
		default = {	"CR":"\r", "LF":"\n", "CRLF":"\r\n", 	\
					"TAB":"\t", "TRUE":True, "FALSE":False,	\
					"NULL":None}
		if len(args) != len(function.args):
			raise CoreException("argument count is error")
		for name in default.keys():
			local_var_list[name] = default[name]
		i = 0
		for name in function.args:
			local_var_list[name] = args[i]
			i = i + 1
		statements = function.statements
		try:
			self.run_statements(statements, local_var_list)
		except ReturnException, e:
			return e.retvalue
