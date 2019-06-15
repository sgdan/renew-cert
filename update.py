#!/usr/local/bin/python

import boto3
import os
from subprocess import call, Popen, PIPE


def read(file):
    """Read a file and return contents as string"""
    with open(file, 'r') as f:
        return f.read()


def write(ssm, key, value):
    """Write string value to ssm secure parameter"""
    ssm.put_parameter(Name=key, Value=value,
                      Type='SecureString', Overwrite=True)


email = os.environ['EMAIL']
region = os.environ['AWS_DEFAULT_REGION']
domain = os.environ['DOMAIN']

ssm = boto3.client('ssm', region_name=region)
prefix = '/cert/' + domain.replace('*', '_')
cert = None
try:
    param = ssm.get_parameter(Name=prefix+'/chain', WithDecryption=True)
    cert = param['Parameter']['Value']
except ssm.exceptions.ParameterNotFound:
    print 'No certificate in SSM'

should_renew = True
if cert:
    # check if cert expires in the next 7 days
    with open(os.devnull, 'w') as devnull:
        sp = Popen(['openssl', 'x509', '-noout', '-checkend',
                    str(7*24*60*60)], stdin=PIPE, stdout=devnull)
    sp.communicate(cert)
    if sp.returncode == 0:
        should_renew = False
        print 'Certificate will not expire in the next 7 days'

if should_renew:
    print 'Renewing certificate...'
    call(['certbot', 'certonly', '-n', '--agree-tos', '--email', email,
          '--dns-route53', '-d', domain])
    trimmed = domain[2:] if domain.startswith('*.') else domain
    folder = '/etc/letsencrypt/live/' + trimmed
    write(ssm, prefix + '/chain', read(folder + '/fullchain.pem'))
    write(ssm, prefix + '/key', read(folder + '/privkey.pem'))
    print 'Certificate data stored in SSM'
