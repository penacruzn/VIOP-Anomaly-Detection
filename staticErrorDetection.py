#You can call this in order to determine errors given static contexts
# all that means is we call this without using machine learning, just inferenced errors

#NOTE while this SHOULD work on uncategorized packets, it performs better for already seperated packets


#####
#   With the other classes in mind, we can call either the specific portion on the classified packets
#   since its never altered, or just pass all the packets in
#
####

# Specifically, we analyze timestamps, if there is a long gap, we assume there is a conneciton error
def latencyError(packets, threshold_ms=200): #default 200, specify otherwise
    #TODO Maybe mess around in case 200ms is too much, but likely this is the one case where an actual
    #connection is busted. Source? I made it up
    errors = 0
    for i in range (1,len(packets)):
        time_diff = (packets[i]['timestamp'] - packets[i-1]['timestamp']).total_seconds() * 1000
        if time_diff > threshold_ms:
            errors+=1
    return errors

# Inspects packets for standard sip errors
def sipErrors(packets):
    errors = 0
    #TODO this can be done better, but this SHOULD work
    #birds nest
    for pkt in packets:
        if pkt['protocol'] == 'SIP':  # Make sure this is a SIP packet (otherwise test is meaningless)
            if 'payload' in pkt:  # this is how we can get the jist of the packet
                sip_payload = pkt['payload'] 

                # TODO add more conditions and ensure this is accurate
                if 'SIP/2.0 4' in sip_payload or 'SIP/2.0 5' in sip_payload or 'SIP/2.0 6' in sip_payload:
                        #we rely on pattern matching, so any error that follows the 4xx, 5xx, or 6xx pattern
                        errors += 1

    return errors

#Inspects for RTCP errors
def rtpErrors(packets):
    #we can check for nacks and what not here
    errors = 0
    for pkt in packets:
        if pkt['protocol'] == 'RTCP':
            #TODO place additional flags here
            if 'nack' in pkt:
                errors +=1

    return errors

# If we are constantly resending packets, there can be an issue
def retryErrors(packets):
    # See duplicated packets, consider flagging as dupicates rather than errors
    seen_packets = set()
    errors = 0
    for pkt in packets:
        #TODO change this to a better identifier if possible
        packet_id = pkt['timestamp'] #this is unique to the packets, so if there is a duplicate thats no good!
        if(packet_id) in seen_packets:
            errors += 1
        else:
            seen_packets.add(packet_id)
    return errors

# This checks for all types of errors
def detectErrors(packets):
    #handler and basic sum for all errors. Good for IP specific
    totalErr = 0
    totalErr += latencyError(packets)
    totalErr += sipErrors(packets)
    totalErr += rtpErrors(packets)
    totalErr += retryErrors(packets)
    return 0