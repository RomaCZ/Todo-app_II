import urllib.request
import urllib.parse
import http.cookiejar
import socket
import gzip
import re
from time import sleep
from random import choice
from dataclasses import dataclass
from hashlib import md5
from pathlib import Path as path
from pathlib import PureWindowsPath as win_path
from ast import literal_eval


@dataclass
class GetUrl:
	""" GetUrl - modul založený na urllib a http 
	""" 

	headers: dict = None
	use_cookies: bool = False
	cookiejar: any = None
	delayed_repeats: tuple = (3, 15, 65)
	status: int = 999
	content: bytearray = bytearray()
	openers: list = None
	user_agents: tuple = (
		'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.19) Gecko/20081202 Firefox (Debian-2.0.0.19-0etch1)',
		'Mozilla/5.0 (X11; U; Linux i686; pl-PL; rv:1.9.0.2) Gecko/20121223 Ubuntu/9.25 (jaunty) Firefox/3.8',
		'Mozilla/5.0 (X11; U; Linux i686; pl-PL; rv:1.9.0.2) Gecko/2008092313 Ubuntu/9.25 (jaunty) Firefox/3.8',
		'Mozilla/5.0 (X11; U; Linux i686; it-IT; rv:1.9.0.2) Gecko/2008092313 Ubuntu/9.25 (jaunty) Firefox/3.8',
		'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2b5) Gecko/20091204 Firefox/3.6b5',
		'Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.2b5) Gecko/20091204 Firefox/3.6b5',
		'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2) Gecko/20091218 Firefox 3.6b5',
		'Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.2b4) Gecko/20091124 Firefox/3.6b4 (.NET CLR 3.5.30729)',
		'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2b4) Gecko/20091124 Firefox/3.6b4',
		'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2b1) Gecko/20091014 Firefox/3.6b1 GTB5',
		'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2a1pre) Gecko/20090428 Firefox/3.6a1pre',
		'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2a1pre) Gecko/20090405 Firefox/3.6a1pre',
		'Mozilla/5.0 (X11; U; Linux i686; ru-RU; rv:1.9.2a1pre) Gecko/20090405 Ubuntu/9.04 (jaunty) Firefox/3.6a1pre',
		'Mozilla/5.0 (Windows; Windows NT 5.1; es-ES; rv:1.9.2a1pre) Gecko/20090402 Firefox/3.6a1pre',
		'Mozilla/5.0 (Windows; Windows NT 5.1; en-US; rv:1.9.2a1pre) Gecko/20090402 Firefox/3.6a1pre',
		'Mozilla/5.0 (Windows; U; Windows NT 5.1; ja; rv:1.9.2a1pre) Gecko/20090402 Firefox/3.6a1pre (.NET CLR 3.5.30729)',
		'Mozilla/5.0 (Windows; U; Windows NT 6.1; ru-RU; rv:1.9.2) Gecko/20100105 MRA 5.6 (build 03278) Firefox/3.6 (.NET CLR 3.5.30729)',
		'Mozilla/5.0 (Windows; U; Windows NT 5.2; zh-CN; rv:1.9.2) Gecko/20100101 Firefox/3.6',
		'Mozilla/5.0 (Windows; U; Windows NT 5.2; zh-CN; rv:1.9.2) Gecko/20091111 Firefox/3.6',
		'Mozilla/5.0 (Windows; U; Windows NT 5.2; rv:1.9.2) Gecko/20100101 Firefox/3.6',
		'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30618; MAXTHON 2.0)',
		'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Trident/4.0; MAXTHON 2.0)',
		'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; MAXTHON 2.0)',
		'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; MAXTHON 2.0)',
		'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; MAXTHON 2.0)',
		'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 1.0.3705; MAXTHON 2.0)',
		'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; InfoPath.1; MAXTHON 2.0)',
		'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; MAXTHON 2.0)',
		'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506; .NET CLR 3.5.21022; MAXTHON 2.0)',
		'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; SLCC1; .NET CLR 2.0.50727; .NET CLR 3.5.21022; .NET CLR 3.5.30729; .NET CLR 3.0.30618; MAXTHON 2.0)',
		'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.8.1.8pre) Gecko/20070928 Firefox/2.0.0.7 Navigator/9.0RC1',
		'Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.8.1.8pre) Gecko/20070928 Firefox/2.0.0.7 Navigator/9.0RC1',
		'Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en-US; rv:1.8.1.8pre) Gecko/20071001 Firefox/2.0.0.7 Navigator/9.0RC1',
		'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.7pre) Gecko/20070815 Firefox/2.0.0.6 Navigator/9.0b3',
		'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.8.1.7pre) Gecko/20070815 Firefox/2.0.0.6 Navigator/9.0b3',
		'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.7pre) Gecko/20070815 Firefox/2.0.0.6 Navigator/9.0b3',
		'Mozilla/5.0 (Macintosh; U; PPC Mac OS X Mach-O; en-US; rv:1.8.1.7pre) Gecko/20070815 Firefox/2.0.0.6 Navigator/9.0b3',
		'Mozilla/5.0 (Windows; U; Windows 98; en-US; rv:1.8.1.5pre) Gecko/20070710 Firefox/2.0.0.4 Navigator/9.0b2',
		'Mozilla/5.0 (Macintosh; U; PPC Mac OS X Mach-O; en-US; rv:1.8.1.5pre) Gecko/20070710 Firefox/2.0.0.4 Navigator/9.0b2',
		'Opera/9.99 (Windows NT 5.1; U; pl) Presto/9.9.9',
		'Opera/9.70 (Linux ppc64 ; U; en) Presto/2.2.1',
		'Opera/9.70 (Linux i686 ; U; zh-cn) Presto/2.2.0',
		'Opera/9.70 (Linux i686 ; U; en-us) Presto/2.2.0',
		'Opera/9.70 (Linux i686 ; U; en) Presto/2.2.1',
		'Opera/9.70 (Linux i686 ; U; en) Presto/2.2.0',
		'Opera/9.70 (Linux i686 ; U; ; en) Presto/2.2.1',
		'Opera/9.70 (Linux i686 ; U; ; en) Presto/2.2.1',
		'Mozilla/5.0 (Linux i686 ; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.70',
		'Mozilla/4.0 (compatible; MSIE 6.0; Linux i686 ; en) Opera 9.70',
		'Opera 9.7 (Windows NT 5.2; U; en)',
		'Opera/9.64(Windows NT 5.1; U; en) Presto/2.1.1',
		'Opera/9.64 (X11; Linux x86_64; U; pl) Presto/2.1.1',
		'Opera/9.64 (X11; Linux x86_64; U; hr) Presto/2.1.1',
		'Opera/9.64 (X11; Linux x86_64; U; en-GB) Presto/2.1.1',
		'Opera/9.64 (X11; Linux x86_64; U; en) Presto/2.1.1',
		'Opera/9.64 (X11; Linux x86_64; U; de) Presto/2.1.1',
		'Opera/9.64 (X11; Linux x86_64; U; cs) Presto/2.1.1',
		'Opera/9.64 (X11; Linux i686; U; tr) Presto/2.1.1',
		'Opera/9.64 (X11; Linux i686; U; sv) Presto/2.1.1',
		'Opera/9.64 (X11; Linux i686; U; pl) Presto/2.1.1',
		'Opera/9.64 (X11; Linux i686; U; nb) Presto/2.1.1',
		'Opera/9.64 (X11; Linux i686; U; Linux Mint; nb) Presto/2.1.1',
		'Opera/9.64 (X11; Linux i686; U; Linux Mint; it) Presto/2.1.1',
		'Opera/9.64 (X11; Linux i686; U; en) Presto/2.1.1',
		'Opera/9.64 (X11; Linux i686; U; de) Presto/2.1.1',
		'Opera/9.64 (X11; Linux i686; U; da) Presto/2.1.1',
		'Opera/9.64 (Windows NT 6.1; U; de) Presto/2.1.1',
		'Opera/9.64 (Windows NT 6.0; U; zh-cn) Presto/2.1.1',
		'Opera/9.64 (Windows NT 6.0; U; pl) Presto/2.1.1',
		'Opera/9.64 (Windows NT 6.0; U; it) Presto/2.1.1',
		'Opera/9.63 (X11; Linux x86_64; U; ru) Presto/2.1.1',
		'Opera/9.63 (X11; Linux x86_64; U; cs) Presto/2.1.1',
		'Opera/9.63 (X11; Linux i686; U; ru) Presto/2.1.1',
		'Opera/9.63 (X11; Linux i686; U; ru)',
		'Opera/9.63 (X11; Linux i686; U; nb) Presto/2.1.1',
		'Opera/9.63 (X11; Linux i686; U; en)',
		'Opera/9.63 (X11; Linux i686; U; de) Presto/2.1.1',
		'Opera/9.63 (X11; Linux i686)',
		'Opera/9.63 (X11; FreeBSD 7.1-RELEASE i386; U; en) Presto/2.1.1',
		'Opera/9.63 (Windows NT 6.1; U; hu) Presto/2.1.1',
		'Opera/9.63 (Windows NT 6.1; U; en) Presto/2.1.1',
		'Opera/9.63 (Windows NT 6.1; U; de) Presto/2.1.1',
		'Opera/9.63 (Windows NT 6.0; U; pl) Presto/2.1.1',
		'Opera/9.63 (Windows NT 6.0; U; nb) Presto/2.1.1',
		'Opera/9.63 (Windows NT 6.0; U; fr) Presto/2.1.1',
		'Opera/9.63 (Windows NT 6.0; U; en) Presto/2.1.1',
		'Opera/9.63 (Windows NT 6.0; U; cs) Presto/2.1.1',
		'Opera/9.63 (Windows NT 5.2; U; en) Presto/2.1.1',
		'Opera/9.63 (Windows NT 5.2; U; de) Presto/2.1.1',
		'Opera/9.63 (Windows NT 5.1; U; pt-BR) Presto/2.1.1',
		'Mozilla/5.0 (Windows; U; Windows NT 5.1; en) AppleWebKit/526.9 (KHTML, like Gecko) Version/4.0dp1 Safari/526.8',
		'Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10_4_11; tr) AppleWebKit/528.4+ (KHTML, like Gecko) Version/4.0dp1 Safari/526.11.2',
		'Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10_4_11; en) AppleWebKit/528.4+ (KHTML, like Gecko) Version/4.0dp1 Safari/526.11.2',
		'Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10_4_11; de) AppleWebKit/528.4+ (KHTML, like Gecko) Version/4.0dp1 Safari/526.11.2',
		'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_6; en-gb) AppleWebKit/528.10+ (KHTML, like Gecko) Version/4.0dp1 Safari/526.11.2',
		'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_4; en-us) AppleWebKit/528.4+ (KHTML, like Gecko) Version/4.0dp1 Safari/526.11.2',
		'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_4; en-gb) AppleWebKit/528.4+ (KHTML, like Gecko) Version/4.0dp1 Safari/526.11.2',
		'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1; .NET CLR 1.1.4322; InfoPath.1; .NET CLR 2.0.50727)',
		'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1; .NET CLR 1.1.4322; InfoPath.1)',
		'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1; .NET CLR 1.1.4322; Alexa Toolbar; .NET CLR 2.0.50727)',
		'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1; .NET CLR 1.1.4322; Alexa Toolbar)',
		'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
		'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.40607)',
		'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1; .NET CLR 1.1.4322)',
		'Mozilla/5.0 (Windows; U; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)',
		'Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)',
		'Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4325)',
		'Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.1)',
		'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
		'Mozilla/4.08 (compatible; MSIE 6.0; Windows NT 5.1)',
		'Mozilla/4.01 (compatible; MSIE 6.0; Windows NT 5.1)',
		'Mozilla/4.0 (X11; MSIE 6.0; i686; .NET CLR 1.1.4322; .NET CLR 2.0.50727; FDM)',
		'Mozilla/4.0 (Windows; MSIE 6.0; Windows NT 6.0)',
		'Mozilla/4.0 (Windows; MSIE 6.0; Windows NT 5.2)',
		'Mozilla/4.0 (Windows; MSIE 6.0; Windows NT 5.0)',
		'Mozilla/4.0 (Windows; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)',
		'Mozilla/4.0 (MSIE 6.0; Windows NT 5.1)',
		'Mozilla/4.0 (MSIE 6.0; Windows NT 5.0)',
		'Mozilla/4.0 (compatible;MSIE 6.0;Windows 98;Q312461)',
		'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 6.0)'
		)
	
	def __post_init__(self):
		
		if not self.openers:
			self.openers = []
		
		if self.use_cookies and not self.cookiejar:
			self.cookiejar = http.cookiejar.CookieJar()
			self.openers.append(
				urllib.request.HTTPCookieProcessor(self.cookiejar))
			
		self.opener = urllib.request.build_opener(*self.openers)
		
		if not self.headers:
			self.opener.addheaders = [
				("Content-type", "application/x-www-form-urlencoded"),
				("User-Agent", choice(self.user_agents))
				]
		else:
			self.opener.addheaders = self.headers

	def get(self, url, data=None):

		sleep(0.3)
		
		for attemp, delay in enumerate(self.delayed_repeats, start=1):

			try:
				if data:
					data = urllib.parse.urlencode(data)
					data = data.encode("ascii")
					self.resource = self.opener.open(url, data, timeout=115)
				else:
					self.resource = self.opener.open(url, timeout=115)
				
				self.status = self.resource.getcode()
				self.content.extend(self.resource.read())
				
			except Exception as error:
				print(f"Chyba stazeni URL: {url}")
				print(f"\tError: {error}")
			
			if self.content:
				break

			print(f"{attemp}. opakovani z celkovych ", end="")
			print(f"{len(self.delayed_repeats)} bude za {delay} sec.")
			sleep(delay)

		else:
			print(f"Finalni chyba stazeni URL: {url}")
			
		return self.content

	def change_user_agent(self, force_agent=None):
		""" User-Agent - by default randomly selected from self.user_agents.
			Could be trigerred again to randomly change.
			Or str of User-Agent could be passed as argument.
		
			change_user_agent() 		--> User-Agent: random(user_agents)
			change_user_agent("test")	--> User-Agent: "test"
		"""
		
		if not force_agent:
			force_agent = choice(self.user_agents)
			
		self.opener.addheaders = [("User-Agent", force_agent)]



class UsedReguest(urllib.request.BaseHandler):
	""" Pass urllib.request (opnener's) headers, data and method to response.

		response.used_method	>>> ["GET", "POST", "HEAD"]
		response.used_data		>>> b"Any data used for reguest"
		response.used_headers	>>> {headers from request.unredirected_hdrs}
	"""

	def default_open(self, request):
		# Let next handler handle the request
		return None 

	def http_response(self, request, response):
		response.used_method = request.get_method()
		response.used_data = request.data
		response.used_headers = request.unredirected_hdrs
		return response
	
	# For http and https alike
	https_response = http_response



class AllowGzipEncoding(urllib.request.BaseHandler):
	""" Add gzip support to urllib.request.
		
		By passing "Accept-Encoding: gzip, deflate" header to request.
		Automatically handle decompression.
	"""

	def default_open(self, request):
		""" Add support for gzip, deflate compression to request headers.
		"""

		preset = request.unredirected_hdrs.get("Accept-Encoding", "")
		preset = preset.split()
		preset.append("gzip, deflate")
		new_encoding = ", ".join(set(filter(None, preset)))
		request.unredirected_hdrs["Accept-Encoding"] = new_encoding

		# Let next handler handle the request
		return None

	def http_response(self, request, response):
		"""	Decompress gzipped response.
			Change encoding to match current content.
		"""
		
		if response.getheader("Content-Encoding") == "gzip":
			response.read_gzip = response.read
			response.read = lambda : gzip.decompress(response.read_gzip())
			response.headers.replace_header("Content-Encoding", "identity")
		return response

	https_response = http_response



class CacheHandler(urllib.request.BaseHandler):
	""" Stores responses in a persistant on-disk cache.
	"""

	def __init__(self, cache="url_cache", gzip=False):
		self.cache = cache
		self.gzip = gzip
		self.file_name = ""

		path(self.cache).mkdir(exist_ok=True) 

	def safe_name(self, url, data):
		""" Set self.file_name suitable for HDD file cache.
			Strips for file system dangerous and common characters.
			Add md5 hash based on URL and request data.
		"""
		
		# From: https://github.com/httplib2/
		# From: http://intertwingly.net/code/venus/

		re_url_scheme = re.compile(r"^\w+://")
		re_unsafe = re.compile(r"[^\w\-_.()=!]+", re.ASCII)

		url_bytes = bytearray()
		url_bytes.extend(url.encode("utf-8"))
		if data:
			url_bytes.extend(data)

		url_md5 = md5(url_bytes).hexdigest()
		file_name = re_url_scheme.sub("", url)
		file_name = re_unsafe.sub("", file_name)

		# Limit length of file name to safe 93 chars (Windows).
		# https://github.com/httplib2/httplib2/pull/74
		# C:\Users\   <username>   \AppData\Local\Temp\ <safe_filename> , <md5>
		# Chars  9  +  max 104   +         20          +       x      + 1 + 32
		# Max = 259 chars, Thus max safe file name x = 93 chars, rounded to 90.
		
		self.file_name = f"{file_name[:90]}_{url_md5}"
		
		if self.gzip:
			self.file_name = f"{self.file_name}_gz"

	def default_open(self, request):
		self.safe_name(request.full_url, request.data)
		self.head_path = path(self.cache, f"{self.file_name}.header")
		self.body_path = path(self.cache, f"{self.file_name}.body")
		request.from_cache = False
		
		if self.head_path.exists() and self.body_path.exists():
			print("Request will be fullfiled from cache.")
			
			body_path_uri = self.body_path.resolve().as_uri()
			request.full_url = body_path_uri
			request.from_cache = True

		# Let next handler handle the request
		return None

	def http_response(self, request, response):
		
		def pack_data(compression, data):
			if compression:
				data = gzip.compress(data)
			return data

		def unpack_data(compression, data):
			if compression:
				data = gzip.decompress(data)
			return data
		
		if request.from_cache:
			response.msg = "OK"
			response.code = 200
			
			head_data = self.head_path.read_bytes()
			head_data = unpack_data(self.gzip, head_data)
			response.headers._headers = literal_eval(head_data)
		else:
			print("Response will be saved to cache.")
			
			head_data = str(response.getheaders()).encode("utf-8")
			self.head_path.write_bytes(pack_data(self.gzip, head_data))
			
			body_data = response.read()
			self.body_path.write_bytes(pack_data(self.gzip, body_data))
			
			response.read = lambda : body_data
		return response

	https_response = http_response



def check_internet(host="8.8.8.8", port=53, timeout=3):
	""" Check internet connectivity by connecting to Google DNS.
		
		Host: 8.8.8.8 (google-public-dns-a.google.com)
		OpenPort: 53/tcp
		Service: domain (DNS/TCP)
	"""
	
	try:
		socket.setdefaulttimeout(timeout)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
		print("Internet available")
		return True
	except Exception as ex:
		print("Internet not available")
		print(ex)
		return False

def check_network():
	""" Check network connectivity by reading current IP adress.
		Wheather it is default 127.0.0.1 means no network.
	"""
	
	ip_address = socket.gethostbyname(socket.gethostname())
	if ip_address == "127.0.0.1":
		print("Network not available")
		return False
	else:
		print(f"Network available, current IP address: {ip_address}")
		return True



if __name__ == "__main__":
	import unittest



	class MyTest(unittest.TestCase):
		def test_user_agent(self):
			# Init with random User-Agent
			url_request = GetUrl()
			agent_a = dict(url_request.opener.addheaders).get("User-Agent")
			# Generate new random User-Agent
			url_request.change_user_agent()
			agent_b = dict(url_request.opener.addheaders).get("User-Agent")
			# agent_a != agent_b
			self.assertNotEqual(agent_a, agent_b)
			
			# Set specific User-Agent
			url_request.change_user_agent("Mozilla/4.0")
			agent_c = dict(url_request.opener.addheaders).get("User-Agent")
			self.assertEqual(agent_c, "Mozilla/4.0")

		def test_login(self):
			url = "http://testing-ground.scraping.pro/login?mode=login"
			data = {"usr": "admin", "pwd": "12345"}
			url_request = GetUrl(use_cookies=True)
			url_request.get(url, data)
			# Check return code 200
			self.assertEqual(url_request.status, 200)
			
			# Check if page confirmed login
			success = r".*<h3 class=\'success\'>WELCOME :\)</h3>.*"
			self.assertRegex(url_request.content.decode(), success)

	unittest.main()
	
	
	
	# from geturl_handlers import CacheHandler
	# url_request = GetUrl(delayed_repeats=(1,), use_cookies=True, openers=[CacheHandler()])
	# url = "http://testing-ground.scraping.pro/login?mode=login"
	# data = {"usr": "admin", "pwd": "12345"}
	# url_request.get(url, data)
	# print(url_request.status)
	# print(url_request.content.decode())
	# print(url_request.cookiejar)
