"""
oauth2client: https://github.com/google/oauth2client

"""
from __future__ import print_function
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import datetime 
import json 
from yaml import load
import urllib2
import time 



class Siame_calendar(object):
	_creds = None; 
	_store = None; # client_secret  
	_google_calendar  = None; # google calendar 
	_scope = "" ; 
	_GMT_OFFSET = "+02:00";
	_event = "";
	_calendar_url = "" ; 
	_couches_basses = None;
	_temp_reel = None;
	_conception_systeme = None;
	_reseau = None;
	_module = None; 
	_week = None;


	def get_json_data(self, raw_txt):

		# searching data 
		for data in raw_txt:	
			if data[0:13] == "v.events.list":
				break ;
		
		# data correction
		data = data[15:-3];
		
		# remoing: /,\,>,<from json data 
		i=0;
		while i < len(data)-1:
			if data[i] == "/" or data[i] == "\\" or data[i] == ">" or data[i] == "<" :		
				data = data[:i] +" "+ data[i+1:];				
			
			i =i+1; 

		# make json_data using load from "yaml" ; 
		js_data = load(data);
		return js_data;

	def get_calendar_data(self):
		responce = urllib2.urlopen(self._calendar_url);
		data = responce.read() ; 
		raw_data = open("raw_data.txt","w");
		raw_data.write(data);
		raw_data.close();

	def create_module_json(self,module):
		 module_json = dict();
		 start_time = dict();
		 end_time = dict();
		 #starting, endig time module ; 
		 start_time['dateTime'] = module["start"]+self._GMT_OFFSET ; 
		 end_time['dateTime'] = module["end"]+self._GMT_OFFSET ;
		 #create module json 
		 module_json["summary"] = module["text"][30:];
		 module_json["start"] = start_time;
		 module_json["end"] = end_time;
		 module_json["colorId"] = "11";
		 
		 return module_json ; 

	def parsing_data(self):
		raw_data = open("raw_data.txt");
		raw_txt = raw_data.readlines();
		#print ("------raw_txt :"+str(raw_txt[5]));
		json_data = self.get_json_data(raw_txt);
		#print (type(json_data));

		for module in json_data:
			#Couches basses 
			if "Couches logicielles basses" in module["text"]:
				self._couches_basses = self.create_module_json(module);
				self._week.append(self._couches_basses);
			#Temps reel ;
			if "TR" in module["text"]:
				self._temp_reel = self.create_module_json(module);
				self._week.append(self._temp_reel);
			# Conception systme materiel 
			if "Conception" in module["text"]:
				self._conception_systeme = self.create_module_json(module);
				self._week.append(self._conception_systeme);
			# Reseaux pour ...
			if "applications" in module["text"]:
				self._reseau = self.create_module_json(module);
				self._week.append(self._reseau);

		raw_data.close();



	def create_event(self, module_list):
		for mod in module_list : 
			e = self._google_calendar.events().insert(calendarId='primary',sendNotifications=True, body=mod).execute()
	

			"""
			print (type(mod));
			print (mod);
			time.sleep(2);
			"""


	def start(self):
		self.get_calendar_data();
		self.parsing_data();
		self.create_event(self._week);
		"""
		print(self._couches_basses); 
		print(self._temp_reel);
		print(self._conception_systeme);
		print(self._reseau)
		"""

	def __init__(self):
		super (Siame_calendar, self).__init__()
		self._week = [] ;
		self._couches_basses = [];
		self._temp_reel =[];
		self._conception_systeme= [];
		self._reseau = [];

		self._scope = 'https://www.googleapis.com/auth/calendar'
		self._calendar_url = "https://edt.univ-tlse3.fr/calendar/default.aspx?View=week&Type=group&ResourceName=formation_EIINSE_s1"
		self._store = file.Storage('storage.json')
		self._creds = self._store.get()
		if not self._creds or self._creds.invalid:
		    flow = client.flow_from_clientsecrets('client_secret.json', self._scope);
		    self._creds = tools.run_flow(flow, self._store)	
		self._google_calendar = discovery.build('calendar', 'v3', http=self._creds.authorize(Http()))


def main():
	myCalendar = Siame_calendar();
	myCalendar.start();


if __name__ == '__main__':
	main()