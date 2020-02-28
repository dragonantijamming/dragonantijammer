import h5py 
from hdf5_utils import *

f = h5py.File('radio.h5','r')

export_all_fields(f,"hd5test")
export_recv_iqdata(f,"hdf5test_iqdata.csv",21) # IQ data from sequence number 21



