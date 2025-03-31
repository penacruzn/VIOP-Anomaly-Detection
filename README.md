# VoIP-CallQual

This program focuses on packet analysis and anomaly detection in order to classify certain connections and direct users to points of interests and potential conflicts within their VoIP network.

## Creators

TODO -- This was originally thought of by @Slopar


## TODO List 

- Currently the GUI is the main class which is fine, but it needs to have the proper connections to the packet gatherer  
- If anyone is interested in training a model, simulating errors, or gathering any sorts of incorrect pcaps for testing  
- StaticErrorDetection could have more checks within it  
- StaticErrorDetection has some dirty checks (i.e., SIP errors are a keyword match, consider a more thorough approach)  
- GUI is okay, but could be nicer  
- The GUI does not automatically update with packets; there are some details in the packet gatherer, but there could be more there  
- If you come up with additional functions, feel free to add them (for example, more in-depth log analysis rather than spitting out all the information)  
- Packet gatherer primarily focuses on SIP packets, can expand to allow additional packets  
- Packet gatherer may be missing fields in the dataframe; if this is the case, add them  
- Buttons on GUI need proper functionality:  
  - Error logs should show error packets  
  - Errors should update properly  
- Additional categories for organization:  
  - While this has been explored and the dictionary should cover this, they are not currently implemented  
- Since this is not tested, we may need to flush the packet gatherer buffer.  

**This is not an exhaustive list. I just came up with these, and there are likely more things that I may gloss over or that may arise during testing.**  

#### Message me with concerns or questions.


## Credits
Wireshark                                                                                                                       
https://wiki.wireshark.org/uploads/__moin_import__/attachments/SampleCaptures/aaa.pcap                                                                                                                              >> This is a usable sample capture to ensure the program works         