#!/usr/bin/env python3
## This script checks to see if the local gateway/s are up, and  ##
## will modify the ospf config to stop advertising a default     ##
## gateway if down.                                              ##

## REQUIREMENTS ## (pip3 install -r requirements.txt)
import argparse
import json
import requests

#import local modules
# -- local ./helpers
from helpers.logging import Logger

## CLI Arguments ##
def arg_parser(version="1.0"):
  """ Args """

  parser = argparse.ArgumentParser(description='Queries gateways and stops advertising default via fr, if down')
  parser.add_argument('-c', '--cert', help='Either a boolean, in which case it controls whether we verify the server’s TLS certificate, or a string, in which case it must be a path to a CA bundle to use. Defaults to False', action='store')
  parser.add_argument('-H', '--host', help='Specify the router hostname or IP.', action='store', required=True)
  parser.add_argument('-k', '--key', help='Specify the api key.', action='store', required=True)
  parser.add_argument('-s', '--secret', help='Specify the api secret.', action='store', required=True)
  parser.add_argument('-l', '--logfile', help='Output a log file', action='store_true')
  parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
  return parser.parse_args()

## VARIABLES ##
args = arg_parser()

def resolve_env_vars():
  global api_key;     api_key = args.key;       logger.debug(f"API key provided")
  global api_secret;  api_secret = args.secret; logger.debug(f"API secret provided")
  global api_host;    api_host = args.host;     logger.debug(f"Router host: {api_host}")


## FUNCTIONS ##
def set_cost(cost):
  # from http.client import HTTPConnection
  # HTTPConnection.debuglevel = 1 if args.verbose else 0
  r = requests.post(
    (f"https://{api_host}/api/quagga/ospfsettings/set"),
    verify = args.cert if args.cert else False,
    json = {"ospf": {"originatemetric": "{cost}"}},
    auth=(api_key, api_secret) 
  )


def remidiate():
  status = query_gateways()
  logger.debug(f"status is: {status}")
  cost = query_ospf_cost()
  logger.debug(f"cost is: {cost}")
  if status == "up":
    if cost == 10:
      logger.debug(f"No change; gateways are up and advertising at desired cost metric of: {cost}")
    else:
      logger.info(f"Updating metric from {cost} to 10")
      set_cost(10)
  elif status == "down":
    if cost == 100:
      logger.debug(f"No change; gateways are DOWN and advertising at desired cost metric of: {cost}")
    else:
      logger.info(f"Updating metric from {cost} to 100")
      set_cost(100)
      
def query_ospf_cost():
  # from http.client import HTTPConnection
  # HTTPConnection.debuglevel = 1 if args.verbose else 0
  r = requests.get(
    (f"https://{api_host}/api/quagga/ospfsettings/get"),
    verify = args.cert if args.cert else False,
    auth=(api_key, api_secret) 
  )

  try:
    response = json.loads(r.text)
    logger.debug(response['ospf'])
  except Exception as e:
    logger.error(response)

  try:
    d = json.dumps(response['ospf'])
    conf = json.loads(d)
    m = conf["originatemetric"]
    logger.debug(f"originatemetric: {m}")
    return int(m)
        
  except Exception as e:
      logger.error(e.args)


def query_gateways():
  # from http.client import HTTPConnection
  # HTTPConnection.debuglevel = 1 if args.verbose else 0
  r = requests.get(
    (f"https://{api_host}/api/routes/gateway/status"),
    verify = args.cert if args.cert else False,
    auth=(api_key, api_secret) 
  )
  try:
    response = json.loads(r.text)
    logger.info(response['items'])
  except Exception as e:
    logger.error(response)
  
  try:
    for i in response['items']:
      if i['status_translated'] == 'Online':
        logger.info(f"At least one gateway is up.")
        return "up"
      else:
        logger.warning(f"Gateways are Down")
        return "down"
  except Exception as e:
      logger.error(e.args)

## MAIN ##
def main():
  resolve_env_vars()
  remidiate()
  
if __name__ == "__main__":
  args = arg_parser()
  level='DEBUG' if args.verbose else 'INFO'
  writeLog=True if args.logfile else False
  logger = Logger(enable_log_file=writeLog, log_level=level).create_logger()
  main()