# We use this class in order to get the packet information

# Either we keep this simple, or we consider separating important information here for further analysis

# Keep pull information / Store the packets somewhere in the case they need to be revisited.

import pyshark
import pandas as pd
from pprint import pprint  # pretty print, it's nicer for debugging

# TODO I think we need to flush the cap buffer as to not duplicate packets on live. 

# This is the brains — we collect packets or we live capture them
class PacketGatherer:
    def __init__(self, source='ExampleCapture/aaa.pcap'):  # default packet to open
        self.source = source  
        self.packets = []
        self.classified = {}
        self.df = pd.DataFrame()  # DataFrame for the processed data

    # Mode specifies the source of packets. Use 'live' or 'file' for your needs
    def gather_packets(self, mode):
        if mode == 'live':
            print("    ⏳ sniffing packets...")
            cap = pyshark.LiveCapture(interface='en0')  # Use en0 for Wi-Fi on Mac
            try:
                for i, packet in enumerate(cap.sniff_continuously(packet_count=10)):  # Grab 10 packets max
                    print(f"    📦 [{i}] Raw packet: {packet}")
                    packet_info = self.process_packet(packet)
                    if packet_info:
                        self.packets.append(packet_info)
            except Exception as e:
                print(f"❌ Error during sniffing: {e}")
            print(f"    ✅ sniff complete. Packets sniffed: {len(self.packets)}")

        elif mode == 'file':  # this is from the specified file above
            cap = pyshark.FileCapture(self.source)
            print(f"    📁 Reading from file: {self.source}")
            for packet in cap:
                packet_info = self.process_packet(packet)
                if packet_info:
                    self.packets.append(packet_info)
            print(f"✅ File packet count: {len(self.packets)}")

        else:
            raise ValueError("Invalid mode. Please use 'live' or 'file'.")

        # Convert to DataFrame
        self.df = pd.DataFrame(self.packets)

        # Debugging output
        if not self.df.empty:
            print("📊 DataFrame created with columns:", self.df.columns.tolist())
            print("📊 Sample data:\n", self.df.tail())
        else:
            print("⚠️ DataFrame is empty — no usable packets processed.")

        self.classify()  # less work outside of this method

    def process_packet(self, packet):
        try:
            packet_info = {
                'timestamp': packet.sniff_time,
                'source_ip': getattr(packet, 'ip', None).src if hasattr(packet, 'ip') else None,
                'destination_ip': getattr(packet, 'ip', None).dst if hasattr(packet, 'ip') else None,
                'protocol': packet.highest_layer,
                'packet_length': len(packet),
                'port': packet[packet.transport_layer].dstport if hasattr(packet, 'transport_layer') else None,
            }
            print("🔍 Packet Info:", packet_info)
            return packet_info
        except Exception as e:
            print(f"❌ Failed to process packet: {e}")
            return None

    def get_Dataframe(self):
        if self.df is not None and not self.df.empty:
            print("📊 Returning DataFrame with columns:", self.df.columns.tolist())
            print("📊 Preview of data:\n", self.df.tail())
        else:
            print("❌ DataFrame is None or empty.")
        return self.df

    def update_Dataframe(self, packet_info):
        self.df = pd.concat([self.df, pd.DataFrame([packet_info])], ignore_index=True)

    def classify(self):
        self.classified = {}

        for pkt in self.packets:
            src_ip = pkt['source_ip']
            if src_ip not in self.classified:
                self.classified[src_ip] = {}

            conn_id = (pkt['destination_ip'], pkt['port'])

            if conn_id not in self.classified[src_ip]:
                self.classified[src_ip][conn_id] = {
                    'sip_packets': [],
                    'rtp_packets': [],
                    'rtcp_packets': [],
                    'other_packets': []
                }

            if pkt['protocol'] == 'SIP':
                self.classified[src_ip][conn_id]['sip_packets'].append(pkt)
            elif pkt['protocol'] == 'RTP':
                self.classified[src_ip][conn_id]['rtp_packets'].append(pkt)
            elif pkt['protocol'] == 'RTCP':
                self.classified[src_ip][conn_id]['rtcp_packets'].append(pkt)
            else:
                self.classified[src_ip][conn_id]['other_packets'].append(pkt)

# Usage test
if __name__ == "__main__":
    packet_gatherer = PacketGatherer("ExampleCapture/aaa.pcap")
    packet_gatherer.gather_packets('live')
    df = packet_gatherer.get_Dataframe()
    print(df.head())
    pprint(packet_gatherer.classified, width=120)
    print("\n" * 10)
