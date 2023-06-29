import os
# change this for production environment
# if there is no ENV variable set for domain_name then set it here
if 'DOMAIN' in os.environ:
    domain_host = os.environ['DOMAIN']
    print("Using domain from environment variable : {}".format(domain_host))
else:
    #domain_host = "tdm.wildc.net"
    domain_host = "localhost"
    print("Using domain from config.py : {}".format(domain_host))