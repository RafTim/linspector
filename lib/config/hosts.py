import re


class Host:
    def __init__(self, name="", host="", parent="", services=None, comment=""):
        self.name = name
        self.host = host
        self.parent = parent
        self.services = services
        self.comment = comment

    def __str__(self):
        ret = "Host('Name: " + self.name + "', 'access: " + self.host + "', "
        if self.parent != "":
            ret += "'parent: " + self.parent + "', "
        ret += "'HostServices: {"
        for s in self.services:
            ret += str(s) + "\n"
        ret += "}"
        return ret


class HostService:
    def __init__(self, service, warning="", critical=""):
        self.service = service
        self.warning = warning
        self.critical = critical

    def setCommand(self, command):
        self.service.command = command

    def getCommand(self):
        return self.service.command

    def __str__(self):
        ret = str(self.service)
        if self.warning:
            ret += "warning: " + str(self.warning)
        if self.critical:
            ret += "critical: " + str(self.critical)
        return ret;


def parseHostList(hosts, services):
    '''parse the HostList and replace any command as nessesary '''
    #precompiled regexPattern which finds replacements in service strings
    pattern = re.compile("@(\w+)")
    #get a List of Host Objects and leave services unparsed for this moment
    parsedHosts = [Host(name, **values) for name, values in hosts.items()]
    #predefined dict to cache service replacements by name
    serviceReplacements = {}
    for host in parsedHosts:
        #list to store HostService Objects
        hostServices = []
        #lets start to parse the Service Dict.
        for servicename, serviceParams in host.services.items():
            #bool to check if the service is defined.
            found = False
            #to a real iteration. just pick the right service
            for service in services:
                if service.name != servicename: continue
                #indicate we found a service
                found = True
                #check to see if we already regexed our service command
                if service.name not in serviceReplacements:
                    serviceReplacements[service.name] = pattern.findall(service.command)
                for params in serviceParams:
                    #copy replacements from service command
                    replacements = serviceReplacements[service.name][:]
                    #for every Host.service.parameter we need a new HostService Object
                    hostService = HostService(service.clone())
                    #check if the ServiceParameter contain warnings or critical values
                    if 'warning' in params:
                        hostService.warning = params['warning']
                        del params['warning']
                    if 'critical' in params:
                        hostService.critical = params['critical']
                        del params['critical']
                        #any remainig parm should be a replacement
                    for parm in params:
                        if parm not in replacements:
                            print "warning: undefined parameter: " + parm + " in host " + host.name + " from service " + service.name
                            continue
                            #replace our ServiceCommand with the parameter_value (search, replacement, string)
                        hostService.setCommand(re.sub('@' + parm, params[parm], hostService.getCommand()))
                        replacements.remove(parm)
                        #host will not be inside ServiceParameters, so check this also
                    if 'host' in replacements:
                        hostService.setCommand(re.sub('@host', host.host, hostService.getCommand()))
                        replacements.remove('host')
                        #replacements should be empty now.
                    #If not we cannot use this command as some values are missing
                    if replacements:
                        print "warning: Hostservice " + servicename + " from host " + host.name + " is ignored because of missing replacements: " + str(
                            replacements)
                    else:
                        #anything ok! add to our valid hostServices
                        hostServices.append(hostService)
                #we could't find the service defined in this host. Service ignored!
            if not found:
                print "warning: Service " + servicename + " not defined in host " + host.name
            #replace host.service member by parsed HostService Objects
        host.services = hostServices
    return parsedHosts

