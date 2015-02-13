#!/usr/bin/env python

import pefile
import sys
import os
import re

def strings(filename):
	pe =  pefile.PE(filename, fast_load=False)

	# The List will contain all the extracted Unicode strings
	#
	strings = list()

	# Fetch the index of the resource directory entry containing the strings
	#
	rt_string_idx = [ entry.id for entry in  pe.DIRECTORY_ENTRY_RESOURCE.entries].index(pefile.RESOURCE_TYPE['RT_STRING'])

	# Get the directory entry
	#
	rt_string_directory = pe.DIRECTORY_ENTRY_RESOURCE.entries[rt_string_idx]

	# For each of the entries (which will each contain a block of 16 strings)
	#
	for entry in rt_string_directory.directory.entries:

	  # Get the RVA of the string data and
	  # size of the string data
	  #
	  data_rva = entry.directory.entries[0].data.struct.OffsetToData
	  size = entry.directory.entries[0].data.struct.Size
	  print >> sys.stderr, 'Directory entry at RVA', hex(data_rva), 'of size', hex(size)

	  # Retrieve the actual data and start processing the strings
	  #
	  data = pe.get_memory_mapped_image()[data_rva:data_rva+size]
	
	  #print data
	  
	  offset = 0
	  while True:
		# Exit once there's no more data to read
		if offset>=size:
		  break
		# Fetch the length of the unicode string
		#
		ustr_length = pe.get_word_from_data(data[offset:offset+2], 0)
		offset += 2
	##
	#    # If the string is empty, skip it
		if ustr_length==0:
		  continue
	#
	#    # Get the Unicode string
	#    #
		ustr = pe.get_string_u_at_rva(data_rva+offset, max_length=ustr_length)
		offset += ustr_length*2
		strings.append(ustr)
		#print >> sys.stderr, 'String of length', ustr_length, 'at offset', offset
		print hex(data_rva+offset),ustr

if len(sys.argv)<2:
	print "Usage: %s <binary>" % sys.argv[0]
	sys.exit()

filename=sys.argv[1]

if not os.path.isfile(filename):
	print "File not found..."
	sys.exit()

s=""
try:
	strings(filename)
except Exception:
	pass

