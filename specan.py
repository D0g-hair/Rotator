#!/usr/bin/env python
#
# matplotlib now has a PolarAxes class and a polar function in the
# matplotlib interface.  This is considered alpha and the interface
# may change as we work out how polar axes should best be integrated

from visa import *
import pyvisa

class SpecAnalyzer():
	
	def __init__(self,status_bar=None,error_msg=None):
		self._status_bar=status_bar
		self._error_msg=error_msg
		self.load_supported()
		self.maxhold=False

	def _status(self,msg):
		if self._status_bar is None:
			pass
		else:
			self._status_bar(str(msg))
	
	def _error(self,msg):
		if self._error_msg is None:
			pass
		else:
			self._error_msg(str(msg))
	
	def open_device(self,device):
		try:
			inst = instrument(device,timeout=2)
		except pyvisa.visa_exceptions.VisaIOError:
			return
		self.instr=inst
		self.device=device
		
	
	def set_frequency(self,center,span):
		"""Only for the 8566B analyzer to change freq
		:param center: Center freq in Hz.
		:param span: Span freq in Hz.
		"""
		self.instr.write('CF '+str(int(center)) + 'HZ;'+'SP ' + str(int(span)) + 'HZ')
	
	def clear_trace(self):
		"""Clear trace, only for the 8566B analyzer
		"""
		self.instr.write('A1')
		if self.maxhold:
			self.instr.write('A2')
		
	def set_max_hold(self,state):
		"""Set the max hold state for the 8566B analyzer
		"""
		self.maxhold=state
		
	def find_device(self):
		"""Find a VISA device that matches a device from the config file.
		:return True - Found a device, False - Did not find a device
		"""
		try:
			self._status("Searching for instruments...")
			id_cmds = ['*IDN?','ID']
			for device in get_instruments_list():
				if device.find("COM") is not -1:
					continue
				inst = instrument(device,timeout=2)
				try:
					for id_cmd in id_cmds:
						inst.write(id_cmd)
						try:
							cur_dev=inst.read()
						except pyvisa.visa_exceptions.VisaIOError as e:
							continue					
						i=0
						for dev in self.supported_dev:
							if cur_dev.find(dev) is not -1:
								self._status("Found Device: " + dev)
								self.device_addr=device
								self.instr = inst
								self.cmds = self.supported_dev_cmd[i]
								return True
							i = i + 1
				except pyvisa.visa_exceptions.VisaIOError as e:
					pass					
					
		except pyvisa.visa_exceptions.VisaIOError as e:
			pass
		self._status("No Device Found")
		return False
		
	def get_peak_power(self):
		"""Return the peak power of the current trace in dBm
		:return Peak Power (dBm)
		"""
		try:
			for cmd in self.cmds:
				self.instr.write(cmd)
			#self.instr.wait_for_srq()
			data=self.instr.read_values()
			return data[0]
		except pyvisa.visa_exceptions.VisaIOError as e:
			self._error(str(e)) #TODO - see what happens if an unhandled exception occurs
				
	def load_supported(self):
		"""
		This function loads a file with the name returned by *IDN? or ID 
		followed by the commands to set and read a peak marker.
		"""
		self.supported_dev=[]
		self.supported_dev_cmd=[]
		self._status("Loading supported files...")
		with open('devices.txt','r+') as f:
				linetype='device'
				cmd=[]
				for line in f:
					if line=='\n' or line == '\n\r' or line == '\r' or line =='\r\n':
						linetype='device'
						self.supported_dev_cmd.append(cmd)
						cmd=[]
					else:
						if linetype is 'device':
							self.supported_dev.append(line.strip())
							linetype = 'cmd'
						elif linetype is  'cmd':
							cmd.append(line.strip())
				self.supported_dev_cmd.append(cmd)

		
						
						
		
	

