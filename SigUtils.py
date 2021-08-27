# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 13:16:41 2021

@author: 3704394
"""

import numpy as np
import struct

LUT_magnitude = {\
                     0:"yocto",\
                     1:"zepto",\
                     2:"atto",\
                     3:"femto",\
                     4:"pico",\
                     5:"nano",\
                     6:"micro",\
                     7:"milli",\
                     8:"",\
                     9:"kilo",\
                     10:"mega",\
                     11:"giga",\
                     12:"tera",\
                     13:"peta"\
                     }

LUT_unit =      {\
                     0:"V",\
                     1:"A",\
                     2:"VV",\
                     3:"AA",\
                     4:"OU",\
                     5:"W",\
                     6:"sqrtV",\
                     7:"sqrtA",\
                     8:"intgrV",\
                     9:"intgrA",\
                     10:"dtV",\
                     11:"dtA",\
                     12:"dtdiv",\
                     13:"Hz",\
                     14:"S",\
                     15:"SA",\
                     16:"pts",\
                     17:"NULL",\
                     18:"DB",\
                     19:"DBV",\
                     20:"DBA",\
                     21:"VPP",\
                     22:"VDC",\
                     23:"DBM"\
                     }

# Horizontal grid, manual says 14         
hgrid = 14

# Not sure what this is, but manual says it's 25
code_per_div = 25
                     
## Just a class to hold a value with a unit, peeled from scope bin files.
## Unit of Value
## Magnitude of value
## Value (either 32bit or 64bit float)
class SigUnit():
    def __init__(self,_bytes):
        self.value,self.magn,self.unit = struct.unpack("<dII",_bytes)
        
    def return_SI(self):
        return self.value * 10**(3*(self.magn-8))
        
    # Only works for py3.7+
    #def tostring(self):
    #    return f"{self.value} {LUT_magnitude[self.magn]}{LUT_unit[self.unit]}"
        
## Attempt to class-warp all relevant features of the Siglent scope binary
class SigWaveForm():
    def __init__(self,_bytes):
        self.ch1,self.ch2,self.ch3,self.ch4 = struct.unpack("<4I",_bytes[:16])
        
        self.ch1_volt_div_val = SigUnit(_bytes[16:32])
        self.ch2_volt_div_val = SigUnit(_bytes[32:48])
        self.ch3_volt_div_val = SigUnit(_bytes[48:64])
        self.ch4_volt_div_val = SigUnit(_bytes[64:80])
        
        self.ch1_vert_offset  = SigUnit(_bytes[80:96])
        self.ch2_vert_offset  = SigUnit(_bytes[96:112])
        self.ch3_vert_offset  = SigUnit(_bytes[112:128])
        self.ch4_vert_offset  = SigUnit(_bytes[128:144])
        
        self.digital_on = struct.unpack("I",_bytes[144:148])[0]
        
        if self.digital_on:
            print("Digital channels not implemented!")
            
        self.time_div         = SigUnit(_bytes[212:228])
        self.time_delay       = SigUnit(_bytes[228:244])
        
        self.wave_length = struct.unpack("<I",_bytes[244:248])[0]
        
        self.sample_rate      = SigUnit(_bytes[248:264])
        
        data_ptr = 0x800
        
        if self.ch1:
            self.ch1_raw = np.array(struct.unpack("<%dB"%self.wave_length,_bytes[data_ptr:data_ptr+self.wave_length]))
            data_ptr += self.wave_length
            
        if self.ch2:
            self.ch2_raw = np.array(struct.unpack("<%dB"%self.wave_length,_bytes[data_ptr:data_ptr+self.wave_length]))
            data_ptr += self.wave_length
    
        if self.ch3:
            self.ch3_raw = np.array(struct.unpack("<%dB"%self.wave_length,_bytes[data_ptr:data_ptr+self.wave_length]))
            data_ptr += self.wave_length
            
        if self.ch4:
            self.ch4_raw = np.array(struct.unpack("<%dB"%self.wave_length,_bytes[data_ptr:data_ptr+self.wave_length]))
            data_ptr += self.wave_length
            
    def t_arr(self):
        return - ( self.time_div.return_SI() * hgrid / 2.) + np.arange(self.wave_length) * 1/self.sample_rate.return_SI() + self.time_delay.return_SI()
        
    def V_arr(self,ch):
        if ch == 1 and self.ch1:
            data         = self.ch1_raw
            volt_div_val = self.ch1_volt_div_val
            vert_offset  = self.ch1_vert_offset
        elif ch==2 and self.ch2:
            data = self.ch2_raw
            volt_div_val = self.ch2_volt_div_val
            vert_offset  = self.ch2_vert_offset
        elif ch==3 and self.ch3:
            data = self.ch3_raw
            volt_div_val = self.ch3_volt_div_val
            vert_offset  = self.ch3_vert_offset
        elif ch==4 and self.ch4:
            data = self.ch4_raw
            volt_div_val = self.ch4_volt_div_val
            vert_offset  = self.ch4_vert_offset
        else:
            raise ValueError("The selected channel is not active!")
            
        return (data-128)*volt_div_val.return_SI()/code_per_div+vert_offset.return_SI()
        
def main():
    global wf
    with open("SDS00001.bin","rb") as f:
        wf = SigWaveForm(f.read())
        
if __name__ == "__main__":
    main()