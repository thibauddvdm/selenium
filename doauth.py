#!/usr/bin/python3

import optparse
import requests
import json
import urllib3
import base64
import stdiomask
import html
import re
import readline
import os
import logging
import datetime
import socket
import smtplib
import ssl
import urllib
import subprocess
import shlex
import tempfile
import mimetypes
from urllib.error import HTTPError
from email.message import EmailMessage
from email.utils import make_msgid

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formatdate

class colors:
    RED = '\033[31m'
    ENDC = '\033[m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
 

def readConsole(prompt, errmsg, func, heading=None, options=None, emptyOK=False):
    if heading:
        print(heading)
    
    if options:
        for key, value in options.items():
            print("\t %s - %s" % (key, value))
            
    while True:
        value = input(prompt)
        
        if emptyOK and (value == None or len(value) == 0):
            return None
        
        if func(value):
            return value
        else:
            print(errmsg % value)
            
def arguments():
    usage = "usage: %prog [-c|--config ] [-p|--properties property-file]"
    parser =  optparse.OptionParser(usage)
    parser.add_option("--config", "-c", help="Configure healthcheck service", action="store_true", dest="config")
    parser.add_option("--properties", "-p", help="Property files", action="store", dest="props")
    
    options, args = parser.parse_args()
    
    if options.props and options.config:
        parser.error(colors.RED + 'Options --config and --properties are mutually exclusive' + colors.ENDC)
    
    return options.props, options.config, True
    
def input_url():   
    regex = re.compile(
        r'^(?:http)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    while True:    
        url = input("Enter management Console URL: ")
        if re.match(regex, url) is not None:
            return url
        else:
            print(f'{colors.RED}Invalid URL: {colors.BLUE}{url}{colors.ENDC}')

def rlinput(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
      return input(prompt)
    finally:
       readline.set_startup_hook()

def authenticate(mcurl, user, password):
    json = {"email": user, "password": password}
    response = requests.post(mcurl + "/api/auth/login", data = json, verify=False)
    json = response.json()
    if response.status_code != 200:
        print(f'{colors.RED}Failed to authenticate to Management Console: {colors.YELLOW}%s {colors.BLUE}%s{colors.ENDC}' % (json['status'], json['message']))
        quit()
    return response.json()["token"]

def create_service(mcurl, token):
    service_name = rlinput("Enter service name: ", "Auth Monitoring")
    service_issuer = rlinput("Enter service issuer: ", "Secret Double Octopus")
    icon_filename = rlinput("Enter icon filename: ", "rest.png")
    
    fn, fextension = os.path.splitext(icon_filename)
    with open(icon_filename, "rb") as image_file:
        encoded = base64.b64encode(image_file.read().strip()).decode('utf-8')
    
    headers = {'Authorization': 'Bearer %s' % token, 'Content-Type': 'application/json'}
    json = {"name": service_name, "type": "REST", "issuer": service_issuer, "icon": f'data:image/{fextension[1:]};base64,{encoded}'}
    
    try:
        response = requests.post(mcurl + "/api/services", headers=headers, json=json, verify=False)
        response.raise_for_status()
        json = response.json()
        return json["id"]
    except HTTPError as http_err:
        print(f'{colors.RED}Failed creating service: {colors.YELLOW}{http_err.code} {colors.BLUE}')
    except Exception as err:    
        print(f'{colors.RED}Failed creating service: {colors.YELLOW}{response.status_code} {colors.BLUE}')
        
    quit()

def select_service(mcurl, token):
    headers = {'Authorization': 'Bearer %s' % token, 'Content-Type': 'application/json'}
    try:
        response = requests.get(mcurl + '/api/directories/explorer/members/search?path=cm9vdCMx&filter=USERS&pageNum=0&pageSize=128', headers=headers, verify=False)
        response.raise_for_status()
        json = response.json()
        print("="*64)
        
        services = []
        i = 1
        for item in json['data']:
            service = { "name": None, "id": None}
            service['name'] = item['name']
            service['id'] = item['id']
            services.append(service)
            print('{:6d}  {}'.format(i, service['name']))
            i += 1
        
        while True:
            index = int(input("Select service index: "))
            if index in range(1, len(services)+1):
                return services[index]['id']
            print("%s  Index out of bounds %s%d%s" % (colors.BLUE, colors.RED, index, colors.ENDC))
    except HTTPError as http_err:
        print(f'{colors.RED}Failed fetching service list: {colors.YELLOW}{http_err} {colors.BLUE}')
    except Exception as err:    
        print(f'{colors.RED}Failed fetching service list: {colors.YELLOW}{err} {colors.BLUE}')       
    quit()


def select_user(mcurl, token, path):
    headers = {'Authorization': 'Bearer %s' % token, 'Content-Type': 'application/json'}
    try:
        response = requests.get(mcurl + '/api/services?pageNum=0&pageSize=128', headers=headers, verify=False)
        response.raise_for_status()
        json = response.json()
        print("="*64)
        
        i = 1
        for datun in json['data']:
            print('{:6d}  {}'.format(i, datum['username']))
            i +=i
        while True:
            index = int(input("Select service index: "))        
            if index in range(1, i+1):
                return json['data'][index-1]['id']
            print("%s  Index out of bounds %s%d%s" % (colors.BLUE, colors.RED, index, colors.ENDC))
    except HTTPError as http_err:
        print(f'{colors.RED}Failed fetching service list: {colors.YELLOW}{http_err} {colors.BLUE}')
    except Exception as err:    
        print(f'{colors.RED}Failed fetching service list: {colors.YELLOW}{err} {colors.BLUE}')             
            
            
def create_user(mcurl, token):
    headers = {'Authorization': 'Bearer %s' % token, 'Content-Type': 'application/json'}
    username = rlinput("Enter new local user name: ", "poke")
    prenom = linput("Enter user first name: ", "poke")
    surname = rlinput("Enter user last name: ", "Auth")
    display = rlinput("Enter user display name: ", "Test")
    email = rlinput("Enter user email: ", "poke@acme.com")
    while True:
        password = stdiomask.getpass(prompt="Enter user password: ", mask='*')
        repeat = stdiomask.getpass(prompt="Re-enter user password: ", mask='*')
        if password == repeat:
            break
        print(f"{colors.RED}Passwords don't match:{colors.ENDC}")
        
        json = {'firstName': prenom, 'lastName': surname, 'displayName': display, 'username': username, 'email': email, 'password': password}
 
    try: 
        response = requests.post(f'{mcurl}/api/directories/1/importMembers', headers=headers, json=json, verify=False)
        response.raise_for_status()
        return response.json()['data'][0]['id']
    except requests.exceptions.HTTPError as errh:
        logging.info("Http Error:", errh)
        print(f'{colors.RED}Failed fetching service list: {colors.YELLOW}{http_err} {colors.BLUE}')     
    except requests.exceptions.ConnectionError as errc:
        logging.info("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        logging.info("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        logging.info("Oops: Something Else",err)   
        print(f'{colors.RED}Failed fetching service list: {colors.YELLOW}{err} {colors.BLUE}')       
    quit()    
    
def config():
    print(f'{colors.GREEN}Welcome to Octopus Server Authentication Service Health script.{colors.ENDC}')
    print(f'{colors.GREEN}' + "="*63 + f'{colors.ENDC}')
    
    if "y" != rlinput("Do you wish to proceed? [y/n]:", "y").lower():
        quit()
    
    # mc_url = input_url()
    # admin = input("Enter admin user name: ")
    # password = stdiomask.getpass(prompt="Enter admin password: ", mask='*')
    mc_url = "https://mc-50.izoard.com:8443"
    admin = "sdo.admin@izoard.com"
    password = "AS2020as!"
    
    token = authenticate(mc_url, admin, password)
    
    if "y" == rlinput("Do you wish to create service? [y/n]: ", "y").lower():
        print('calling create service')
        sid = create_service(mc_url, token)
    else:
        print('calling select service')
        sid = select_service(mc_url, token)
    print('Service ID: {:d}'.format(sid))
    
    if "y" == rlinput("Do you wish to a local user? [y/n]: ", "y").lower():
        uid = create_user(mc_url, token)
    else:
        uid = selectUser(mc_url, token)
    

def load_properties(propfile):
    print('In properties load')
        
    if propfile is None:
        propfile = os.path.splitext(__file__)[0] + '.properties'

    print(f'Reading properties from {propfile}')
    props = {}
    with open(propfile, "rt") as F:
        for line in F:
            l = line.strip()
            if l and not l.startswith('#'):
                kv = l.split('=')
                key = kv[0].strip()
                value = '='.join(kv[1:]).strip().strip('"')
                props[key] = value
    return props                


def preauth(url, servicekey, apiversion):
    body = {'serviceKey': servicekey}
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(f'{url}/{apiversion}/preauth', headers=headers, json=body, verify=False)
        response.raise_for_status()
        payload = base64.b64decode(response.json()['payload']).decode('utf-8')
        return 0, json.loads(payload)['authToken']
    except requests.exceptions.HTTPError as errh:
        logging.info("Http Error:", errh)
        return 1, errh
    except requests.exceptions.ConnectionError as errc:
        return 2, logging.info("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        return 2, logging.info("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        logging.info("Oops: Something Else",err)
    


def auth(url, version, username, message, token ):
    headers = {'Content-Type': 'application/json'}
    payload = {'username': username, 'message': message, 'authToken': token}
    print(payload)
    token = None
    try:
        print(f'{url}/{version}/auth')
        response = requests.post(f'{url}/{version}/auth', headers=headers, json=payload, verify=False) 
        response.raise_for_status()
        payload = base64.b64decode(response.json()['payload']).decode('utf-8')
        if not isinstance(payload, dict):
            payload = json.loads(payload)
        print(payload)
        print(type(payload))
        print(f"Returning {payload['authStatus']}")
        return 0, payload['authStatus']
    except requests.exceptions.HTTPError as errh:
        logging.info("Http Error:", errh)
        return 1, errh
    except requests.exceptions.ConnectionError as errc:
        logging.info("Error Connecting:",errc)
        return 2, errc
    except requests.exceptions.Timeout as errt:
        logging.info("Timeout Error:",errt)
        return 2, errt
    except requests.exceptions.RequestException as err:
        logging.info("Oops: Something Else",err)
        return 2, err
    
              
def healthcheck(props):
    print('In healthckeck')
    rc, token = preauth(props['URL'], props['SERVICE_KEY'], props['API_VERSION'])
    if rc != 0:
        return rc, []
    print(f'Token: {token}')
    
    return auth(props['URL'], props['API_VERSION'], props['USERNAME'], props['MESSAGE'], token)


def build_content(template, props, variables):
    with open(template, 'r', encoding='unicode_escape') as T:
        content = T.read()
    
    for v in variables:
        content=re.sub(f"\${{{v}}}", props[v], content)
        
    return content



def build_message(props, plaintext, html):
    msg = EmailMessage()

    # generic email headers
    msg['Subject'] = props['SMTP_SUBJECT']
    msg['From'] = f"{props['FROM']} <{props['SMTP_FROM']}>"
    msg['To'] = f"{props['TO']} <{props['SMTP_TO']}>" 

    # set the plain text body
    msg.set_content(plaintext)

    # now create a Content-ID for the image
    image_cid = make_msgid(domain='izoard.com')
    # if `domain` argument isn't provided, it will 
    # use your computer's name
    
    # set an alternative html body
    msg.add_alternative(html.format(image_cid=image_cid[1:-1]), subtype="html") 
    
    with open('octopus.png', 'rb') as img:
        maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')
        print(f'maintype: {maintype}, subtype: {subtype}')
        
        msg.get_payload()[1].add_related(img.read(), maintype=maintype, subtype=subtype, cid=image_cid)
  

    
    FH, path = tempfile.mkstemp()
    with os.fdopen(FH, 'w') as tmp:
        tmp.write(msg.as_string())
    tmp.close()
    print(f'Message in {path}')
    
    # return path
    return msg, path
   

def sendmail(props, msg, file):

    print(f"Sending message file... {file}")
    curl = f"curl -s {props['SMTP_URL']} --mail-from {props['SMTP_FROM']} --mail-rcpt {props['SMTP_TO']} --ssl -u {props['SMTP_CREDENTIALS']} -T {file} -k --anyauth -v"
    print(curl)
    args = shlex.split(curl)
    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode('utf-8'))
    
    # context = ssl.create_default_context()
    
    # try:
        # parsedURL = urllib.parse.urlparse(props['SMTP_URL'])
        # server = smtplib.SMTP(parsedURL.hostname, parsedURL.port)
        # server.ehlo()
        # server.starttls(context=context)
        # username, password = props['SMTP_CREDENTIALS'].split(':')
        # server.login('chent@b7networks.com', 'oqmdbmalxmtclzmo')
        # server.set_debuglevel(True)
        # server.sendmail(props['SMTP_TO'], 'chent@b7networks.com', msg)
        # # server.sendmail(props['SMTP_TO'], props['SMTP_FROM'], msg)

        # print('Sending...')
        # # with smtplib.SMTP('localhost') as s:
            # # s.send_message(msg)
    # except Exception as e:
        # # Print any error messages to stdout
        # print(e)


    
def main():

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    prop_file, do_config, verbose = arguments()
    
    logfile = os.path.splitext(__file__)[0] + '.log'
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(filename=logfile, level=level)

    
    if do_config:
        config()
        exit(0)
        
    props = load_properties(prop_file)
    print(props)
        
    rc, status = healthcheck(props)
    
    props['NOW'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    props['TARGET'] = urllib.parse.urlparse(props['URL']).hostname
    props['DETAILS'] = status

    props['HOSTNAME'] = socket.gethostname()
    if status == 'accept': 
        props['OUTCOME'] = 'Success'
    else:
        if rc == 2:
            props['OUTCOME'] = '<span style="font-size:12.0pt;font-family:Roboto;color:#ff0000">Failure</span>'
        else:
            props['OUTCOME'] = '<span style="font-size:12.0pt;font-family:Roboto;color:#FF6347">Warning</span>'

    
    html = build_content('template.html', props, ['TO', 'TARGET', 'NOW', 'OUTCOME', 'HOSTNAME', 'DETAILS'])

    plaintext = build_content('template.text', props, ['TO', 'TARGET', 'NOW', 'OUTCOME', 'HOSTNAME', 'DETAILS'])
    msg, email_file = build_message(props, plaintext, html)
    
    print(f"Created message file... {email_file}")
    sendmail(props, msg, email_file)
    

if __name__ == "__main__":
    main()	