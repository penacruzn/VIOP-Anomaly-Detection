
import pyshark
import pandas as pd
from pprint import pprint
from packetGatherer import PacketGatherer
import staticErrorDetection as SED

#this is the testing class // Reference this for usage and imports

if __name__ == "__main__":
    packet_gatherer = PacketGatherer()

    # For live data, loop these
    packet_gatherer.gather_packets('file')

    df = packet_gatherer.get_Dataframe()
    print(df.head())

    # Check classified data 
    pprint(packet_gatherer.classified, width=120) #Use this for printing (MUCH nicer to look at, pretty print)

    print("\n\n\n\n\n\n\n\n\n")

    #Test errors (super general test)
    print(SED.detectErrors(packet_gatherer.packets))
