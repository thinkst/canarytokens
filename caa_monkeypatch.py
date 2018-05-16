# We need to monkey patch support for CAA Records because it is a newish DNS record type
# that is required by the lets encrypt process. Basically we need to respond to CAA record
# requests with anything besides a SERVFAIL, hence we respond with an NXDomain response.

def monkey_patch_caa_support():
    patchDNSModule()
    patchCommonModule()
    patchResolveModule()


def patchDNSModule():
    import twisted.names.dns
    twisted.names.dns.CAA = 257
    twisted.names.dns.QUERY_TYPES[twisted.names.dns.CAA] = "CAA"


def patchCommonModule():
    import twisted.names.common
    twisted.names.common.typeToMethod[twisted.names.dns.CAA] = 'lookupCAA'
    def lookupCAA(self, name, timeout=None):
        return self._lookup(name, twisted.names.dns.IN, twisted.names.dns.CAA, timeout)
    

    twisted.names.common.ResolverBase.lookupCAA = lookupCAA


def patchResolveModule():
    import twisted.names.resolve
    from twisted.names import error
    from twisted.internet import defer
    def lookupCAA(self, name, timeout=None):
        if not self.resolvers:
            return defer.fail(error.DomainError())
        d = self.resolvers[0].lookupCAA(name, timeout)
        for r in self.resolvers[1:]:
            d = d.addErrback(
                twisted.names.resolve.FailureHandler(r.lookupCAA, name, timeout)
            )
        return d
    
    twisted.names.resolve.ResolverChain.lookupCAA = lookupCAA