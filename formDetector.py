import Tkinter as tk
import urlparse
from OptionsWnd import scrolledFrame, AppSettingDialog
import re
import cookielib
import urllib2
import pprint
import CustomRegEx
import collections
getAttrDict = CustomRegEx.ExtRegexParser.getAttrDict


def escapeXml(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').encode('utf-8')
def unescapeXml(s): return s.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').decode('utf-8')

def getFormFieldsData(formHtml, formFields=None):
    if formFields is None:
        formFields = collections.OrderedDict()
    htmlFormElements = "fieldset|input|textarea|select|datalist"
    pattern = r'(?#<form<__TAG__="%s"=tag name=name>*>)' % htmlFormElements
    for m in CustomRegEx.finditer(pattern, formHtml):
        tag, name = m.groups()
        attr = getAttrDict(m.group(), 0, noTag=True)
        attr.pop('*ParamPos*')
        if formFields.has_key(name):
            assert tag == 'input'
            value = formFields[name].get('value', None)
            if value and isinstance(value, basestring):
                value = [value]
                formFields[name]['__TAG__'] = 'select'
                formFields[name]['default'] = value[0] if formFields[name].has_key('checked') else ''
            value.append(attr['value'])
            formFields[name]['value'] = value
            if attr.has_key('checked'):
                formFields[name]['default'] = attr['value']
            continue
        if tag == 'input':
            pass
        elif tag in ['textarea', 'label']:
            attr['value'] = attr.get('*', '')
        elif tag == 'select':
            options = CustomRegEx.findall(r'(?#<option value=value *=&lvalue&>)', m.group())
            attr['value'] = [x[0] for x in options]
            attr['lvalue'] = [x[1] for x in options]
            try:
                selected = CustomRegEx.findall(r'(?#<option selected="selected" value=value>)', m.group())
            except:
                selected = []
            attr['default'] = selected[0] if selected else ''
        elif tag == 'fieldset':
            legend = CustomRegEx.search(r'(?#<legend *=legend>)', m.group())
            if legend:
                legend = legend.group('legend')
                name = 'legend%s' % len(formFields)
                formFields[name] = {'__TAG__':'legend', 'value':legend}
            fieldset = m.group()
            pini = fieldset[1:].find('<')
            pfin = -len('</fieldset>')
            formFields = getFormFieldsData(fieldset[pini:pfin], formFields)
        else:
            continue
        formFields[name] = attr
    return formFields

def getFormData(comPattern, content, posini):
    if not isinstance(comPattern, CustomRegEx.ExtRegexObject): raise TypeError('Expecting an CustomRegEx.ExtRegexObject')
    match = comPattern.search(content, posini)
    if not match: return None
    posfin = match.end()
    formHtml = match.group()
    formAttr = getAttrDict(formHtml, 0, noTag=False)[1]
    formAttr.pop('*ParamPos*')
    formFields = collections.OrderedDict()
    if formAttr and formAttr.has_key('id'):
        formId = formAttr['id']
        pattern = r'''\$\(['"]<input/>['"]\)\.attr\(\{(?P<input_attr>[^}]+)\}\)\.prependTo\(['"]#%s['"]\)''' % formId
        prependVars = re.findall(pattern, content)
        for avar in prependVars:
            avar = avar.replace(': ', ':').replace(',', '').replace(':', '=')
            avar = '<input ' + avar + ' prepend="">'
            attr = getAttrDict(avar, 0, noTag=True)
            name = attr['name']
            formFields[name] = attr
    formFields = getFormFieldsData(formHtml, formFields)

    posini = 0
    datalists = dict([(formFields[key]['list'], key) for key in formFields if formFields[key].has_key('list')])
    comPattern = CustomRegEx.compile(r'(?#<datalist id=id>)')
    while True:
        match = comPattern.search(formHtml, posini)
        if not match: break
        dlist = match.group('id')
        if datalists.has_key(dlist):
            name = datalists[dlist]
            options = CustomRegEx.findall(r'(?#<option value=value>)', match.group())
            formFields[name]['lvalues'] = options
            formFields[name]['value'] = [str(x) for x in range(1, len(options) + 1)]
            formFields[name]['default'] = options[0]
            formFields[name]['__TAG__'] = 'datalist'

        posini = match.end()

    ids = dict([(formFields[key]['id'], key) for key in formFields if formFields[key].has_key('id')])
    labels = CustomRegEx.findall(r"(?#<label for=id *=label>)", formHtml)
    for itemId, label in labels:
        if not ids.has_key(itemId): continue
        name = ids[itemId]
        formFields[name]['label'] = label
    return posfin, formAttr, formFields

def getFormXmlStr(content):
    form_xml ='<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n<settings>\n'
    pattern = r'(?#<form>)'
    comPattern = CustomRegEx.compile(pattern)
    k = 0
    posIni = 0
    while True:
        formData = getFormData(comPattern, content, posIni)
        if not formData: break
        posIni, formAttr, formFields = formData
        formAttr = dict([(key, escapeXml(value)) for key, value in formAttr.items()])
        form_xml += '\t<category label="Form %s">\n' % (k + 1)
        if formAttr:
            form_xml += '\t\t<setting type="lsep" label ="Form attributes"/>\n'
            for name, value in sorted(formAttr.items()):
                form_xml += '\t\t<setting id="fa_{0}" type="text" label="{0}" default="{1}" enable="false"/>\n'.format(name, value)
        bFlag = 0
        for key in formFields:
            if formFields[key].has_key('prepend'):
                if bFlag == 0:
                    bFlag = 1
                    form_xml += '\t\t<setting type="lsep" label ="Form Prepend Vars"/>\n'
            else:
                if bFlag < 2:
                    bFlag = 2
                    form_xml += '\t\t<setting type="lsep" label ="Form Vars"/>\n'
            tag = formFields[key]['__TAG__']
            atype = formFields[key].get('type', '')
            if not isinstance(formFields[key].get('value', ''), basestring):
                formFields[key]['__TAG__'] = 'select'

            if tag == 'input':
                formFields[key]['label'] = formFields[key].get('label', None) or formFields[key].get('name')
                if atype == 'hidden':
                    felem = '<setting id="{name}" type="text" label="{label}" default="{value}" enable="false"/>\n'
                elif atype in ['radio', 'checkbox']:
                    formFields[key]['checked'] = 'true' if formFields[key].has_key('checked') else 'false'
                    felem = '<setting id="{name}" type="bool" label ="{label}" default="{checked}"/>\n'
                elif atype == 'text':
                    formFields[key]['value'] = formFields[key].get('value', '')
                    felem = '<setting id="{name}" type="text" label="{label}" default="{value}"/>\n'
                elif atype == 'submit':
                    formFields[key]['value'] = formFields[key].get('name')
                    felem = '<setting type="lsep" label ="{value}" noline="true"/>\n'
                elif atype == 'file':
                    formFields[key]['defaultValue'] = formFields[key].get('defaultValue', '')
                    felem = '<setting id="if_{name}" type="file" label="{label}" default="{defaultValue}"/>'
                else:
                    formFields[key]['value'] = formFields[key].get('value', '')
                    felem = '<setting id="{name}" type="text" label="{label}" default="{value}"/>\n'
            elif tag == 'datalist':
                formFields[key]['label'] = formFields[key].get('label', None) or formFields[key].get('name')
                formFields[key]['lvalues'] = '|'.join(formFields[key]['lvalues'])
                felem = '<setting id="{name}" type="labelenum" label="{label}" default="{default}" lvalues="{lvalues}"/>\n'
            elif tag == 'select':
                toEscape = ['name', 'value', 'default']
                formFields[key]['value'] = '|'.join(formFields[key]['value'])
                if formFields[key].has_key('lvalue'):
                    formFields[key]['lvalue'] = '|'.join(formFields[key]['lvalue'])
                    toEscape.append('lvalue')
                formFields[key]['default'] = formFields[key].get('default', '')
                formFields[key].update([(fkey, escapeXml(formFields[key][fkey])) for fkey in toEscape])
                if formFields[key].has_key('lvalue'):
                    felem = '<setting id="{name}" type="drpdwnlst" label="{name}" lvalues="{lvalue}" values="{value}" default="{default}"/>\n'
                else:
                    felem = '<setting id="{name}" type="labelenum" label="{name}" lvalues="{value}" default="{default}"/>\n'
            elif tag == 'legend':
                felem = '<setting type="lsep" label="{value}"/>\n'
            else:
                continue
            try:
                form_xml += '\t\t' + felem.format(**formFields[key])
            except:
                pprint.pprint(formFields[key])
                print felem
        form_xml += '\t</category>\n'
        k += 1
    form_xml += '</settings>\n'
    return form_xml

def getFormDataOLD(comPattern, content, posini):
    if not isinstance(comPattern, CustomRegEx.ExtRegexObject): raise TypeError('Expecting an CustomRegEx.ExtRegexObject')
    match = comPattern.search(content, posini)
    if not match: return None
    posfin = match.end()
    formHtml = match.group()
    formAttr = getAttrDict(formHtml, 0, noTag=False)[1]
    formAttr.pop('*ParamPos*')
    formFields = collections.OrderedDict()
    if formAttr and formAttr.has_key('id'):
        formId = formAttr['id']
        pattern = r'''\$\(['"]<input/>['"]\)\.attr\(\{(?P<input_attr>[^}]+)\}\)\.prependTo\(['"]#%s['"]\)''' % formId
        prependVars = re.findall(pattern, content)
        for avar in prependVars:
            avar = avar.replace(': ', ':').replace(',', '').replace(':', '=')
            avar = '<input ' + avar + ' prepend="">'
            attr = getAttrDict(avar, 0, noTag=True)
            name = attr['name']
            formFields[name] = attr
    htmlFormElements = "input|textarea|label|fieldset|legend|select|datalist"
    pattern = r'(?#<form<__TAG__="%s"=tag name=name>*>)' % htmlFormElements
    for m in CustomRegEx.finditer(pattern, formHtml):
        tag, name = m.groups()
        p1, p2 = m.span()
        attr = getAttrDict(m.group(), 0, noTag=True)
        attr.pop('*ParamPos*')
        if formFields.get(name, None):
            if 'value' in attr and formFields[name].has_key('value'):
                value = formFields[name]['value']
                if isinstance(value, basestring):
                    value = [value]
                value.append(attr['value'])
                formFields[name]['value'] = value
        else:
            formFields[name] = attr
            if attr.has_key('list'):
                pattern = r'(?#<datalist id="%s"<value=value>*>)' % attr['list']
                attr['value'] = CustomRegEx.findall(pattern, formHtml)
                pass
            elif tag == 'select':
                pattern = r'(?#<option value=value *=&lvalue&>)'
                match = CustomRegEx.findall(pattern, formHtml[p1:p2])
                # attr['value'] = map(operator.itemgetter(0), match)
                # attr['lvalue'] = map(operator.itemgetter(1), match)
                attr['value'], attr['lvalue'] = match.groups()
                pattern = r'(?#<option value=value>)'
                attr['value'] = CustomRegEx.findall(pattern, formHtml[p1:p2])

                pattern = r'(?#<option value=value selected>)'
                try:
                    attr['default'] = CustomRegEx.findall(pattern, formHtml[p1:p2])[0]
                except:
                    attr['default'] = ''
                pass
            elif tag == 'textarea':
                attr['value'] = attr.get('*', '')
                continue
                pass

    return posfin, formAttr, formFields

def getFormXmlStrOLD(content):
    form_xml ='<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n<settings>\n'
    pattern = r'(?#<form>)'
    comPattern = CustomRegEx.compile(pattern)
    k = 0
    posIni = 0
    while True:
        formData = getFormData(comPattern, content, posIni)
        if not formData: break
        posIni, formAttr, formFields = formData
        formAttr = dict([(key, escapeXml(value)) for key, value in formAttr.items()])
        form_xml += '\t<category label="Form %s">\n' % (k + 1)
        if formAttr:
            form_xml += '\t\t<setting type="lsep" label ="Form attributes"/>\n'
            for name, value in sorted(formAttr.items()):
                form_xml += '\t\t<setting id="fa_{0}" type="text" label="{0}" default="{1}" enable="false"/>\n'.format(name, value)
        bFlag = 0
        for key in formFields:
            if formFields[key].has_key('prepend'):
                if bFlag == 0:
                    bFlag = 1
                    form_xml += '\t\t<setting type="lsep" label ="Form Prepend Vars"/>\n'
            else:
                if bFlag < 2:
                    bFlag = 2
                    form_xml += '\t\t<setting type="lsep" label ="Form Vars"/>\n'
            if isinstance(formFields[key].get('value', ''), basestring):
                formFields[key].update([(fkey, escapeXml(formFields[key][fkey])) for fkey in ['name', 'value', 'checked'] if formFields[key].has_key(fkey)])
                atype = formFields[key].get('type', '')
                if atype == 'hidden':
                    felem = '<setting id="{name}" type="text" label="{name}" default="{value}" enable="false"/>\n'
                    pass
                elif atype in ['radio', 'checkbox']:
                    formFields[key]['checked'] = 'true' if formFields[key].has_key('checked') else 'false'
                    felem = '<setting id="{name}" type="bool" label ="{name}" default="{checked}"/>\n'
                    pass
                elif atype == 'text':
                    formFields[key]['value'] = formFields[key].get('value', '')
                    felem = '<setting id="{name}" type="text" label="{name}" default="{value}"/>\n'
                elif atype == 'submit':
                    felem = '<setting type="lsep" label ="{value}" noline="true"/>\n'
                elif atype == 'file':
                    formFields[key]['defaultValue'] = formFields[key].get('defaultValue', '')
                    felem = '<setting id="if_{name}" type="file" label="{name}" default="{defaultValue}"/>'
                else:
                    formFields[key]['value'] = formFields[key].get('value', '')
                    felem = '<setting id="{name}" type="text" label="{name}" default="{value}"/>\n'
            else:
                toEscape = ['name', 'value', 'default']
                formFields[key]['value'] = '|'.join(formFields[key]['value'])
                if formFields[key].has_key('lvalue'):
                    formFields[key]['lvalue'] = '|'.join(formFields[key]['lvalue'])
                    toEscape.append('lvalue')
                formFields[key]['default'] = formFields[key].get('default', '')
                formFields[key].update([(fkey, escapeXml(formFields[key][fkey])) for fkey in toEscape])
                if formFields[key].has_key('lvalue'):
                    felem = '<setting id="{name}" type="drpdwnlst" label="{name}" lvalues="{lvalue}" values="{value}" default="{default}"/>\n'
                else:
                    felem = '<setting id="{name}" type="labelenum" label="{name}" lvalues="{value}" default="{default}"/>\n'
            form_xml += '\t\t' + felem.format(**formFields[key])
        form_xml += '\t</category>\n'
        k += 1
    form_xml += '</settings>\n'
    return form_xml

def getCurlCommand(baseUrlStr, formAttr, formFields, otherOptions = ''):
    if formAttr.has_key('action'):
        baseUrlStr = urlparse.urljoin(baseUrlStr, formAttr['action'])
    if formAttr.get('method', 'POST').upper() != 'POST':
        otherOptions += ' --get'
        pass
    datafrm = '--data-urlencode "%s=%s"'
    if formAttr.get('enctype', '').lower() == 'multipart/form-data':
        datafrm = '--form "%s=%s"'
        pass
    postData = ' '.join(datafrm % (item[0], str(item[1]).encode('utf-8')) for item in formFields)
    return 'curl "{0}" {1} {2} --compressed'.format(baseUrlStr, postData, otherOptions)

if __name__ == '__main__':
    def openUrl(urlToOpen, validate = False):
        headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'}

        urlToOpen, custHdr = urlToOpen.partition('<headers>')[0:3:2]
        custHdr = custHdr or {}
        if custHdr:
            custHdr = urlparse.parse_qs(custHdr)
            for key in custHdr:
                headers[key] = custHdr[key][0]

        urlToOpen, data = urlToOpen.partition('<post>')[0:3:2]
        data = data or None

        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        try:
            req = urllib2.Request(urlToOpen, data, headers)
            url = opener.open(req)
        except:
            import xbmcgui
            dialog = xbmcgui.Dialog()
            dialog.notification('Url error', 'It was imposible to locate Url', xbmcgui.NOTIFICATION_INFO, 5000)
            toReturn = None
        else:
            if validate:
                toReturn = url.geturl()
            else:
                data = url.read()
                if "text" in url.headers.gettype():
                    encoding = None
                    if 'content-type' in url.headers:
                        content_type = url.headers['content-type'].lower()
                        match = re.search('charset=(\S+)', content_type)
                        if match: charset = match.group(1)
                    charset = encoding or 'iso-8859-1'
                    data = data.decode(charset, 'replace')
                toReturn = (url.geturl(), data)
            url.close()
        return toReturn

    baseUrl = 'https://lastpass.com/?ac=1&lpnorefresh=1'
    baseUrl = 'http://www.bvc.com.co/pps/tibco/portalbvc/Home/Mercados/enlinea/acciones?action=dummy'
    # content = openUrl(baseUrl)[1]

    content = """
<form action="action_page.php">
  <input list="browsers" name="datalist">
  <datalist id="browsers">
    <option value="Internet Explorer">
    <option value="Firefox">
    <option value="Chrome">
    <option value="Opera">
    <option value="Safari">
  </datalist>
</form>
    """

    content = """
<form action="action_page.php">
    <select name="cars">
        <option value="volvo">Volvo</option>
        <option value="saab">Saab</option>
        <option value="fiat">Fiat</option>
        <option value="audi">Audi</option>
    </select><br>
</form>
    """


    Root = tk.Tk()
    # Root.withdraw()
    form_xml = getFormXmlStr(content)
    print(form_xml)
    browser = AppSettingDialog(Root, form_xml, isFile = False, settings = {}, title = 'Form Detector In Develovment', dheight = 600, dwidth = 800)
    print('***Result***')
    pprint.pprint(browser.result)
    print('***AllSettings***')
    pprint.pprint(browser.allSettings)
    if browser.allSettings:
        formAttr = dict([(key[3:], str(value)) for key, value in browser.allSettings if key.startswith('fa_')])
        formFields = [item for item in browser.allSettings if not item[0].startswith('fa_')]
        pprint.pprint(formAttr)
        pprint.pprint(formFields)
        print getCurlCommand(baseUrl, formAttr, formFields)

    Root.mainloop()





