#!/usr/bin/env python

from numpy import *
 
chl_fname=      '/Users/Your_NetID/data/tutorial_data/mon_swf2006/A20060602006090_mar_chlor_a_f999x999.avg'
fish_fname=     '/Users/Your_NetID//rsclass/data/fish_track_data.txt'
new_fish_fname= '/Users/Your_NetID//rsclass/data/fish_track_data_out.txt'


# read in the chlor satallite file...
f = open(chl_fname, 'r')				   
chl_img = fromfile(f, dtype=float32)   	  
f.close()					  
chl_img = chl_img.reshape([999, 999])  
 					    

# read in the tab delimted text files of station informaiton..
f1= open(fish_fname,'r')
all_lines= f1.readlines()  		 
f1.close()

header_line= all_lines[0].strip()  #first line in the List if lines is the header (remote '\n')
all_lines=all_lines[1:]	           #remove header line from the List of lines

 
#open a new file for text output...
f2= open(new_fish_fname,'w')
f2.write(header_line + '\tchl\n')

for i in range(len(all_lines)):
       
    one_line= all_lines[i].strip()
    one_split_line= one_line.split('\t')
    year=    one_split_line[0]
    jday=    one_split_line[1]
    hr=      one_split_line[2]
    lat=     float(one_split_line[3])
    lon=     float(one_split_line[4])
    fish_id= one_split_line[5]
    
    # need to convert lat/lon to row/column
    # need to read in 'station_chl' values at row/col location of satellite data
    
    f2.write(one_line + '\t' + str(station_chl[i]) + '\n')
    
    
f2.close()
 


