import collections
collections.Callable = collections.abc.Callable


from bs4 import BeautifulSoup
from functools import wraps



class BeautifulSoupMakeTag:
	""" Pomocná třída pro BeautifulSoup k vytváření HTML tagů.
		Používá interní html parser Pythonu.

		class_     --> element["class"]
		string_    --> element.string
		parent_    --> parent_.append(element)
		httpequiv_ --> kwargs["http-equiv"]

		Vše ostatní bude rovnou automaticky přidáno do kwargs.
	"""

	def __init__(self):
		self.BeautifulSoup_new_tag = BeautifulSoup("", "html.parser").new_tag

	def new_tag(self, *args, **kwargs):
		class_ = kwargs.pop("class_", None)
		string_ = kwargs.pop("string_", None)
		parent_ = kwargs.pop("parent_", None)
		
		httpequiv_ = kwargs.pop("httpequiv_", None)
		if httpequiv_:
			kwargs["http-equiv"] = httpequiv_

		element = self.BeautifulSoup_new_tag(*args,
					**{k:v for k,v in kwargs.items() if v})

		if class_:
			element["class"] = class_
		if string_:
			element.string = str(string_)
		if parent_:
			parent_.append(element)

		return element

bs_new = BeautifulSoupMakeTag().new_tag


def debug_decorator(vebrose=True):
	""" Postupně zavolá funkce (step_a, step_b a step_c)
		z obalené třídy. Jednotlivé kroky popíše v HTML
		podoby do "debug_container".

		vebrose=True  --> důkladný popis výsledku (default)
		vebrose=False --> pouze Ok jako popis správného výsledku
	"""
	
	def func_decorator(func):
		@wraps(func)
		def func_wrapper(arg, arg_decorator):
			debug_func = func(arg)

			bs_new("div",
				class_="block",
				string_="%s:%s" % (func.__name__, func.__doc__),
				parent_=arg_decorator)

			try:
				bs_new("span", string_="krok_a", parent_=arg_decorator)
				debug_a = debug_func.step_a()
				if not debug_a:
					raise Exception("hodnota je None")
				bs_new("span",
					class_="ok",
					string_="Ok",
					parent_=arg_decorator)

				bs_new("span", string_="krok_b", parent_=arg_decorator)
				debug_b = debug_func.step_b(debug_a)
				if not debug_b:
					raise Exception("hodnota je None")
				bs_new("span",
					class_="ok",
					string_="Ok",
					parent_=arg_decorator)

				if str(type(debug_b)) == "<class 'bs4.element.Tag'>":
					debug_b["class"] = "marked"

				bs_new("span", string_="krok_c", parent_=arg_decorator)
				debug_c = debug_func.step_c(debug_b)
				if not debug_c:
					raise Exception("hodnota je None")
				bs_new("span",
					class_="ok",
					string_=debug_c if vebrose else "Ok",
					parent_=arg_decorator)

			except Exception as error:
				bs_new("span",
					class_="fail",
					string_=error,
					parent_=arg_decorator)

				debug_c = None

			return debug_c

		return func_wrapper

	return func_decorator