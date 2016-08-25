from queries import *
import settings


domains = settings.DOMAINS
nxdomains = settings.NXDOMAINS
google_api_key = settings.GOOGLE_API_KEY
path_elements = ['about','feedback','static','terms','articles','images',\
                 'tags','traffic']
pages = ['index.html','contact.php','post.jsp','submit.aspx']

print '[x] Adding domains'
for d in domains:
    add_canary_domain(domain=d)
    print '\t{domain}'.format(domain=d)

print '[x] Adding NX domains'
for d in nxdomains:
    add_canary_nxdomain(domain=d)
    print '\t{domain}'.format(domain=d)

print '[x] Adding path elements'
for pe in path_elements:
    add_canary_path_element(path_element=pe)
    print '\t{pe}'.format(pe=pe)

print '[x] Adding pages'
for p in pages:
    add_canary_page(page=p)
    print '\t{p}'.format(p=p)

print '[x] Adding google api key'
for k in google_api_key:
    add_canary_google_api_key(key=k)
    print '\t{k}'.format(k=k)
