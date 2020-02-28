# HDF5 UTILS
import h5py
import csv 

""" hdf_utils
This is a collection of utilities that you can use to get information
from dragonradio HDF-5 (.hd5) files. HDF-5 is a file standard based 
on tree-like storage of data, where you have a root node, and each
child of that node is either a -group- of other nodes or is a
-dataset- which "caps off" that branch. Dragonradio log files produce
five datasets in the main group:
    event       Events that occur, with timestamps
    recv        Received packets: has iq data, sequence numbers, etc 
    selftx      ?
    send        Sent packets: similar format to recv 
    slots       Timestamped IQ data 
    snapshots   Snapshots

Methods include [for datafield "X", (e.g. X=recv) and hd5 file 'file']:
    print_datasets(file)
    export_all_fields(file,csvbasename)
    export_recv_iqdata(file,csvname,seqnumber,tmin=0.00)
    print_X_format(file)
    export_X(file,csvname)

"""



""" print_datasets 
    Print the available datasets at the toplevel for h5py.File 
    object f.

    Parameters:
        f       h5py.File object with read access
"""
def print_datasets(f):
    print(list(f.keys()))

# Helper functions for looking at the datafields
def print_event_format(f):
    events = f['event']
    print(events.dtype)

def print_recv_format(f):
    recvs = f['recv']
    print(recvs.dtype)

def print_selftx_format(f):
    selftxs = f['selftx']
    print(selftxs.dtype)

def print_send_format(f):
    sends = f['send']
    print(sends.dtype)

def print_slots_format(f):
    slots = f['slots']
    print(slots.dtype)

def print_send_format(f):
    snapshots = f['snapshots']
    print(snapshots.dtype)

""" export_datafield
    Creates a csv file containing the datafield data 

    Parameters:
        datag   h5py File object
        csvname Name of csv file to write (will overwrite)
"""
def export_datafield(datag,csvname):
    ndata = datag.shape[0]

    with open(csvname,'w',newline='') as csvf:
        writer = csv.writer(csvf, delimiter=',')

        # The first row will be headers
        writer.writerow(list(datag.dtype.names))

        # Now write in the data, converting bytes to strings when possible
        dd = []
        for i in range(0,ndata):
            for j in range(0,len(datag.dtype.names)):
                if type(datag[i][j]) == bytes:
                    dd.append(datag[i][j].decode('utf-8'))
                else:
                    dd.append(datag[i][j])
            writer.writerow(dd)
            dd = []
""" export_event 
    Creates a csv file containing the events with timestamps

    Parameters:
        f       h5py File object
        csvname Name of csv file to write (will overwrite)
"""
def export_event(f,csvname):
    events = f['event']
    export_datafield(events,csvname)


""" export_recv
    Creates a csv file containing the received stuff

    Parameters:
        f       h5py File object
        csvname Name of csv file to write (will overwrite)
"""
def export_recv(f,csvname):
    recvs = f['recv']
    export_datafield(recvs,csvname)

""" export_selftx
    Creates a csv file containing the selftx stuff

    Parameters:
        f       h5py File object
        csvname Name of csv file to write (will overwrite)
"""
def export_selftx(f,csvname):
    selftxs = f['selftx']
    export_datafield(selftxs,csvname)


""" export_send 
    Creates a csv file containing the sends stuff

    Parameters:
        f       h5py File object
        csvname Name of csv file to write (will overwrite)
"""
def export_send(f,csvname):
    sends = f['send']
    export_datafield(sends,csvname)

""" export_slots
    Creates a csv file containing the slots stuff

    Parameters:
        f       h5py File object
        csvname Name of csv file to write (will overwrite)
"""
def export_slots(f,csvname):
    slots = f['slots']
    export_datafield(slots,csvname)

""" export_snapshots
    Creates a csv file containing the snapshots 

    Parameters:
        f       h5py File object
        csvname Name of csv file to write (will overwrite)
"""
def export_snapshots(f,csvname):
    snapshots = f['snapshots']
    export_datafield(snapshots,csvname)

""" export_all_fields
    Export all fields to csv files with base names csvbasename 
"""
def export_all_fields(f,csvbasename):
    export_event(f,csvbasename+"_event.csv")
    export_recv(f,csvbasename+"_recv.csv")
    export_selftx(f,csvbasename+"_selftx.csv")
    export_send(f,csvbasename+"_send.csv")
    export_slots(f,csvbasename+"_slots.csv")
#   export_snapshots() Skip this for now

""" export_recv_iqdata
Save the IQ data corresponding to a packet sequence number seqnumber 
and occuring after timestamp tmin
"""
def export_recv_iqdata(f,csvname,seqnumber,tmin=0.00):
    recvs = f['recv']
    tstampidx = recvs.dtype.names.index("timestamp")
    seqidx = recvs.dtype.names.index("seq")
    iqidx = recvs.dtype.names.index("iq_data")
    
    # Index the hard way
    tstamps = []
    seqs = []
    iqs = []
    for i in range(0,recvs.shape[0]):
        tstamps.append(recvs[i][tstampidx])
        seqs.append(recvs[i][seqidx])
        iqs.append(recvs[i][iqidx])
    
    # Now get the desired data
    # Magic to get first timestamp after tmin
    tminidx = next(i for i,val in enumerate(tstamps) if val>tmin)

    # Remove data before tmin
    tstamps = tstamps[tminidx:]
    seqs = seqs[tminidx:]
    iqs = iqs[tminidx:]

    # Find first matching seq number
    packetidx = seqs.index(seqnumber)
    
    with open(csvname,'w') as csvf:
        writer = csv.writer(csvf,delimiter=',')
        
        tstamp_str = "Timestamp: "+str(tstamps[packetidx])
        sequence_str = "Sequence number: "+str(seqnumber)

        writer.writerow(["Real","Imaginary",tstamp_str,sequence_str])
        iqdata = iqs[packetidx]
        for iq in iqdata:
            writer.writerow([iq.real,iq.imag])


