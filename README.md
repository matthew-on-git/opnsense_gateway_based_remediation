# opnsense_gateway_based_remediation
This script checks to see if the local gateway/s are up, and will modify the ospf config to stop advertising a default gateway if down. 
```
usage: gateway_check.py [-h] [-c CERT] -H HOST -k KEY -s SECRET [-l] [-v]

Queries gateways and stops advertising default via fr, if down

optional arguments:
  -h, --help            show this help message and exit
  -c CERT, --cert CERT  Either a boolean, in which case it controls whether we verify the server’s TLS certificate, or a string, in which case it must be a path to a CA bundle to use. Defaults to False
  -H HOST, --host HOST  Specify the router hostname or IP.
  -k KEY, --key KEY     Specify the api key.
  -s SECRET, --secret SECRET
                        Specify the api secret.
  -l, --logfile         Output a log file
  -v, --verbose         Verbose output
  ```