import demistomock as demisto  # noqa: F401
from CommonServerPython import *  # noqa: F401

keys = [r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
        r"HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Run",
        r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Active Setup\Installed Components",
        r"HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Active Setup\Installed Components",
        r"HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
        r"HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunOnce"]


def Reg2Markdown(baseKey, regResp):
    res, mdRows = [], ''
    if isError(regResp[0]):
        res += regResp
    elif len(regResp) > 1:
        contents = 'Unexpected output from D2RegQuery - more than one entry returned:\n' + '\n'.join([str(x) for x in regResp])
        res.append({'Type': entryTypes['error'], 'ContentsFormat': formats['text'],
                   'Contents': contents})
    else:
        subkeys = regResp[0]['Contents']
        for sk in subkeys:
            if type(subkeys[sk]) == dict:
                for ssk in subkeys[sk]:
                    mdRows += '\n|' + str(baseKey) + '\\' + str(sk) + '|' + str(ssk) + '|' + str(subkeys[sk][ssk]) + '|'
            else:
                mdRows += '\n|' + str(baseKey) + '|' + str(sk) + '|' + str(subkeys[sk]) + '|'
    return (res, mdRows)


res = []
if 'system' in demisto.args():
    system = demisto.args()['system']
elif 'using' in demisto.args():
    system = demisto.args()['using']
else:
    demisto.results({'Type': entryTypes['error'], 'ContentsFormat': formats['text'],
                    'Contents': 'You must provide "system" or "using" as arguments.'})
    sys.exit(0)
mdTable = '### Results for short registry probe of system *' + system + '*'
mdTable += '\n|Key|SubKey|Value|'
mdTable += '\n|-----|------|-----|'
for k in keys:
    regPath = NormalizeRegistryPath(k)
    cmdResp = demisto.executeCommand('D2RegQuery', {'using': system, 'regpath': regPath})
    moreEntries, moreRows = Reg2Markdown(regPath, cmdResp)
    mdTable += moreRows
    res += moreEntries
res.append({'Type': entryTypes['note'], 'ContentsFormat': formats['markdown'], 'Contents': mdTable})
demisto.results(res)
