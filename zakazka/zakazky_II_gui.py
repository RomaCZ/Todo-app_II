#!/usr/local/bin/python
# -*- coding: utf-8 -*- 


from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QTextCharFormat, QColor, QTextCursor
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QThread
from PyQt5.QtCore import QDate
from zakazky_II_ui import Ui_MainWindow

import re
import sys
import time
import traceback
import subprocess
from datetime import datetime, timedelta
from functools import wraps

from bs4 import BeautifulSoup
from geturl_II import geturl
from vestnik2url import old_vestnik2url_list, vestnik2url_list
from nuts import parse_nuts
from bs_clean import clean_html
from old_zakazky import old_zakazka2dict
from zakazky_II_html import make_html, zakazka_dict2html

import ssl
import certifi

ssl._create_default_https_context = ssl._create_unverified_context



import zakazky_II

class WorkerSignals(QObject):
	"""
	Defines the signals available from a running worker thread.
	Supported signals are:

	finished
		No data

	error
		"tuple" (exctype, value, traceback.format_exc())

	result
		"object" data returned from processing, anything

	callback
		"dict" anything
	"""

	finished = pyqtSignal()
	error = pyqtSignal(tuple)
	result = pyqtSignal(object)
	callback = pyqtSignal(object)

class Worker(QObject):
	"""
	Worker thread

	:param callback:
		The function callback to run on this worker thread.
		Supplied args and kwargs will be passed through to the runner.

	:type callback:
		function

	:param args:
		Arguments to pass to the callback function

	:param kwargs:
		Keywords to pass to the callback function
	"""

	def __init__(self, fn, *args, **kwargs):

		print("Worker init")

		super(Worker, self).__init__()
		# Store constructor arguments (re-used for processing)
		self.fn = fn
		self.args = args
		self.kwargs = kwargs
		self.signals = WorkerSignals()

		# Add the callback to our kwargs
		kwargs["callback"] = self.signals.callback

	@pyqtSlot()
	def run(self):
		"""
		Initialise the runner function with passed args, kwargs.
		"""

		print("Worker run")

		# Retrieve args/kwargs here; and fire processing using them
		try:
			result = self.fn(*self.args, **self.kwargs)
		except:
			traceback.print_exc()
			exctype, value = sys.exc_info()[:2]
			self.signals.error.emit((exctype, value, traceback.format_exc()))
		else:
			self.signals.result.emit(result)  # Return the result of the processing
		finally:
			self.signals.finished.emit()  # Done

class MainWindow(QMainWindow, Ui_MainWindow):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent=parent)
		self.setupUi(self)


		todayStyle = QTextCharFormat()
		todayStyle.setFontWeight(500)
		todayStyle.setFontPointSize(12.0)
		todayStyle.setFontUnderline(True)
		todayStyle.setForeground(QColor(30, 144, 255))

		qtToday = QDate.currentDate()
		pyYesterday = datetime.now() - timedelta(days=1)
		qtYesterday = QDate.fromString(
						pyYesterday.strftime("%Y-%m-%d"),
						"yyyy-MM-dd"
						)

		self.headerDate.setText(f"spuštěno: {qtToday.toString('dd/MM/yyyy')}")

		self.calendarFrom.setDateTextFormat(qtToday, todayStyle)
		self.calendarFrom.selectionChanged.connect(self.calendarChanged)
		self.calendarFrom.setSelectedDate(qtYesterday)

		self.calendarTo.setDateTextFormat(qtToday, todayStyle)
		self.calendarTo.selectionChanged.connect(self.calendarChanged)
		self.calendarTo.setSelectedDate(qtYesterday)

		self.buttonStart.clicked.connect(self.thread_start)

		# Pass the function to execute
		# Any other args, kwargs are passed to the run function
		self.worker = Worker(self.fn_execute)
		self.worker.signals.callback.connect(self.fn_callback)
		self.worker.signals.result.connect(self.fn_output)
		self.worker.signals.finished.connect(self.thread_complete)

		# Execute
		self.thread = QThread()
		self.worker.moveToThread(self.thread)
		self.thread.started.connect(self.worker.run)

	def thread_start(self):
		self.thread.keepRunning = True
		self.toolBox.setItemEnabled(0, False)
		self.toolBox.setItemEnabled(1, False)
		
		self.panelSearchInfoReset()

		self.buttonStart.setText("Stop!")
		self.buttonStart.clicked.disconnect(self.thread_start)
		self.buttonStart.clicked.connect(self.thread_stop)
		
		readable_date = "%s - %s" % (self.pyDateFrom.strftime("%d/%m/%Y"), self.pyDateTo.strftime("%d/%m/%Y"))
		self.html, self.left_panel, self.debug_panel, self.right_panel = make_html(search_date=readable_date)
		self.debug_panel.append(zakazky_II.get_aktuality())

		self.thread.start()

	def thread_stop(self):
		self.thread.keepRunning = False
		self.buttonStart.setText("Ukončuji proces...")
		print("Noted thread to quit.")

	def fn_execute(self, callback):
		callback.emit({"urlProgressMax": 6})
		
		zakazky_old = old_vestnik2url_list(self.pyDateFrom, self.pyDateTo)
		callback.emit({"oldZakazkyCount": len(zakazky_old)})

		zakazky = vestnik2url_list(
			self.pyDateFrom, self.pyDateTo,
			contract_type={"ContractType": "WORKS"}
			)
		callback.emit({"zakazkyCount": len(zakazky)})
		
		projektovky = vestnik2url_list(
			self.pyDateFrom, self.pyDateTo,
			contract_type={"ContractType": "SERVICES"}
			)
		callback.emit({"projektovkyCount": len(projektovky)})
		
		url_list = zakazky_old + zakazky + projektovky
		callback.emit({"urlListProgressMax": len(url_list)})
		print(len(url_list))
		
		for i, url in enumerate(url_list, start=1):
			if not self.thread.keepRunning:
				return "fn_execute --> Stopped"
			callback.emit({
				"urlProgress": 1,
				"urlListProgress": i,
				"text": url
				})
			print(i, url)
			
			content = geturl(url)
			callback.emit({"urlProgress": 2})
			
			soup_all = BeautifulSoup(content, "html.parser")
			callback.emit({"urlProgress": 3})
			
			while "<h3>Chyba při zpracování požadavku</h3>" in str(soup_all):
				
				print("Pokus znovu")
				time.sleep(5)
				content = geturl(url)
				soup_all = BeautifulSoup(content, "html.parser")
			
				
				
			
			
			soup = soup_all.find("div", id="content")
			callback.emit({"urlProgress": 4})
			
			if "old.vestnikverejnychzakazek.cz" in url:
				zakazka_dict = old_zakazka2dict(soup, url)
			else:
				zakazka_dict = zakazky_II.zakazka2dict(soup, url)
			callback.emit({"urlProgress": 5})

			#print(zakazka_dict)
			
			if zakazka_dict.get("druh_formulare", "") == "Oznámení o změně":
				callback.emit({"urlProgress": 6})
				time.sleep(0.3)
				continue
			if zakazka_dict.get("druh_formulare", "").startswith("Oznámení o výsledku"):
				callback.emit({"urlProgress": 6})
				time.sleep(0.3)
				continue
			callback.emit({"urlProgress": 6})
			self.left_panel.append(zakazka_dict2html(zakazka_dict))
			
			#time.sleep(0.5)
		
		return "fn_execute --> Done"

	def fn_callback(self, state):
		if state.get("urlProgress", False):
			self.zakazkaProgressBar.setValue(state["urlProgress"])
		if state.get("urlListProgress", False):
			self.zakazkyProgressBar.setValue(state["urlListProgress"])
		
		if state.get("text", False):
			self.textBrowser.append(state["text"])
			self.textBrowser.moveCursor(QTextCursor.End)
		
		if state.get("urlProgressMax", False):
			self.zakazkaProgressBar.setMaximum(state["urlProgressMax"])
		if state.get("urlListProgressMax", False):
			self.zakazkyProgressBar.setMaximum(state["urlListProgressMax"])
		
		if state.get("oldZakazkyCount", False):
			self.oldZakazazkyCountLcd.setEnabled(True)
			self.oldZakazazkyCountLcd.setProperty(
				"intValue", state["oldZakazkyCount"]
				)
		if state.get("zakazkyCount", False):
			self.zakazkyCountLcd.setEnabled(True)
			self.zakazkyCountLcd.setProperty(
				"intValue", state["zakazkyCount"]
				)
		if state.get("projektovkyCount", False):
			self.projektovkyCountLcd.setEnabled(True)
			self.projektovkyCountLcd.setProperty(
				"intValue", state["projektovkyCount"]
				)
		

	def fn_output(self, s):
		print(s)
		if self.thread.keepRunning:
			self.textBrowser.append("<b>Hotovo</b>")
		else:
			self.textBrowser.append("<b>Přerušeno uživatelem</b>")
		self.textBrowser.append("")
		self.textBrowser.moveCursor(QTextCursor.End)

	def thread_complete(self):
		print("Thread complete.")
		self.buttonStart.clicked.disconnect(self.thread_stop)
		self.buttonStart.clicked.connect(self.thread_start)
		self.calendarChanged() # Just to title button Start
		self.toolBox.setItemEnabled(0, True)
		self.toolBox.setItemEnabled(1, True)
		self.thread.quit()
		
		with open("zakazky_II_html.html", mode="w", encoding="utf-8") as file:
			file.write(str(self.html))

	def calendarChanged(self):
		self.pyDateFrom = self.calendarFrom.selectedDate().toPyDate()
		self.pyDateTo = self.calendarTo.selectedDate().toPyDate()

		dateFrom = self.pyDateFrom.strftime('%d/%m/%Y')
		dateTo = self.pyDateTo.strftime('%d/%m/%Y')

		self.toolBox.setItemText(0, f"Vyhledávání od: {dateFrom}")
		self.toolBox.setItemText(1, f"Vyhledávání do: {dateTo}")

		self.buttonStart.setText(f"Vyhledávání od {dateFrom} do {dateTo}")
		self.buttonStart.setStyleSheet("color: black")
		self.buttonStart.setEnabled(True)

		if self.pyDateFrom > self.pyDateTo:
			self.buttonStart.setText(
				"Nelze vyhledat --> 'od' je později než 'do'"
				)
			self.buttonStart.setStyleSheet("color: red")
			self.buttonStart.setEnabled(False)
	
	def panelSearchInfoReset(self):
		self.zakazkyCountLcd.setProperty("intValue", 0)
		self.zakazkyCountLcd.setEnabled(False)
		self.projektovkyCountLcd.setProperty("intValue", 0)
		self.projektovkyCountLcd.setEnabled(False)
		self.oldZakazazkyCountLcd.setProperty("intValue", 0)
		self.oldZakazazkyCountLcd.setEnabled(False)
		self.zakazkaProgressBar.setProperty("value", 0)
		self.zakazkyProgressBar.setProperty("value", 0)


# install_certifi.py
#
# sample script to install or update a set of default Root Certificates
# for the ssl module.  Uses the certificates provided by the certifi package:
#       https://pypi.python.org/pypi/certifi

import os
import os.path
import ssl
import stat
import subprocess
import sys

STAT_0o775 = ( stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
             | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP
             | stat.S_IROTH |                stat.S_IXOTH )


def main_ssl():
    openssl_dir, openssl_cafile = os.path.split(
        ssl.get_default_verify_paths().openssl_cafile)

    # +++> if already done  <----
    #print(" -- pip install --upgrade certifi")
    #subprocess.check_call([sys.executable,
    #    "-E", "-s", "-m", "pip", "install", "--upgrade", "certifi"])

    import certifi
    # change working directory to the default SSL directory
    os.chdir(openssl_dir)
    relpath_to_certifi_cafile = os.path.relpath(certifi.where())
    print(" -- removing any existing file or link")
    try:
        os.remove(openssl_cafile)
    except FileNotFoundError:
        pass
    print(" -- creating symlink to certifi certificate bundle")
    os.symlink(relpath_to_certifi_cafile, openssl_cafile)
    print(" -- setting permissions")
    os.chmod(openssl_cafile, STAT_0o775)
    print(" -- update complete")




if __name__ == "__main__":
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
