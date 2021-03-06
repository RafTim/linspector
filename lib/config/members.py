import re


class Member:
    def __init__(self, nameid, name="", phone="", comment="", parent="", filters=None):
        self.nameid = nameid
        self.name = name
        self.phone = phone
        self.filters = filters
        self.comment = comment
        self.parent = parent

    def __str__(self):
        ret = "Member Id: " + self.nameid + " Name: " + self.name + " Filters: " + str(self.phone)
        for f in self.filters:
            ret += str(f)
        return ret


class MemberFilter:
    def __init__(self, filt, Value):
        self.filt = filt
        self.value = Value

    def __str__(self):
        return "Filter:" + str(self.filter) + " Value:" + self.value


def parseMemberList(members, filters):
    parsedMembers = [Member(nameid, **values) for nameid, values in members.items()]
    for member in parsedMembers:
        mFilter = []
        for filtername, replacement in member.filters.items():
            found = False
            for filt in filters:
                if filt.name != filtername: continue
                found = True
                memberFilter = filt.clone()
                memberFilter.command = re.sub('@member', replacement, filt.command)
                mFilter.append(memberFilter)
            if not found:
                print "warning: filter: " + filtername + " is not defined in member " + member.name
        member.filters = mFilter
    return parsedMembers
