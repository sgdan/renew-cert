#!/usr/local/bin/python

import boto3
import os
from subprocess import call, Popen, PIPE

# Read a file and return contents as string
def read(file):
    with open(file, 'r') as f:
        return f.read()

# Write string value to ssm secure parameter
def write(ssm, key, value):
    ssm.put_parameter(Name=key, Value=value, Type='SecureString', Overwrite=True)

email = os.environ['EMAIL']
region = os.environ['AWS_REGION']
domain = os.environ['DOMAIN']

ssm = boto3.client('ssm')
prefix = '/cert/' + domain.replace('*', '_')
should_renew = True
try:
    # print 'looking for param:', prefix + '/chain'
    param = ssm.get_parameter(Name=prefix+'/chain', WithDecryption=True)
    cert = param['Parameter']['Value']

    # check if cert expires in the next 7 days
    with open(os.devnull, 'w') as devnull:
        sp = Popen(['openssl', 'x509', '-noout', '-checkend', str(7*24*60*60)], stdin=PIPE, stdout=devnull)
    sp.communicate(cert)
    if sp.returncode == 0:
        should_renew = False
        print 'Certificate will not expire in the next 7 days'
except:
    print 'No certificate in SSM'

if should_renew:
    print 'Renewing certificate...'
    call(['certbot', 'certonly', '-n', '--agree-tos', '--email', email,
        '--dns-route53', '-d', domain])
    trimmed = domain[2:] if domain.startswith('*.') else domain
    folder = '/etc/letsencrypt/live/' + trimmed
    write(ssm, prefix + '/chain', read(folder + '/fullchain.pem'))
    write(ssm, prefix + '/key', read(folder + '/privkey.pem'))
    print 'Certificate data stored in SSM'
