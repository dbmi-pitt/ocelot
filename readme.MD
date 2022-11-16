# Ocelot
Obtains census tract and Walk Score for a set of geocoordinates.

## To call
```
python ocelot.py (full path to input file)
```
## Note 
Geocoordinates that correspond to the home address of a study participant constitute **Patient Identifying
Information** (PII). Without an explicit waiver or approval from the UPMC IRB, geocoordinates should not be used as
arguments to endpoints of public APIs.

This notebook will demonstrate proof of concept using the address for DBMI:

5607 Baum Boulevard, Suite 500
Pittsburgh, PA 15206-3701
(40.4581259,-79.9352492)