# -*- mode: Python ; coding: utf-8 -*-
# Copyright (c) 2014 Luca Panno <panno.luca@gmail.com>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

'''
ABC notation to MP3, music integration addon for Anki 2.

Code is based on / inspired by libanki's LaTeX integration and Andreas Klauer's LilyPond integration.
'''

# --- Imports: ---
from anki.hooks import addHook, wrap
from anki.lang import _
from anki.utils import call, checksum, stripHTML, tmpfile
from aqt import mw
from aqt.qt import *
from aqt.utils import getOnlyText, showInfo
from htmlentitydefs import entitydefs
import cgi, os, re, shutil

# --- Globals: ---

# http://abcnotation.com/

abcFile = tmpfile("abc", ".abc")
midFile = tmpfile("abc", ".mid")
wavFile = tmpfile("abc", ".wav")
mp3File = tmpfile("abc", ".mp3")
abc2midiCmd = ["abc2midi", abcFile, "-o", midFile]
timidityCmd = ["timidity", midFile, "-Ow", "-o", wavFile]
lameCmd = ["lame", wavFile, "-b64", mp3File]
abcPattern = "%ANKI%"
abcSplit = "%%%"
abcTemplate = u"""X:1
M:4/4
L:1/4
K:C
%s
""" % (abcPattern,)
abcTemplates = {}
abcDir = os.path.join(mw.pm.addonFolder(), "abc")
abcRegexp = re.compile(r"\[abc(|=([a-z0-9_-]+))\](.+?)\[/abc\]", re.DOTALL | re.IGNORECASE)
abcFieldRegexp = re.compile(r"abc(|-([a-z0-9_-]+))$", re.DOTALL | re.IGNORECASE)
abcNameRegexp = re.compile(r"^[a-z0-9_-]+$", re.DOTALL | re.IGNORECASE)
abcCache = {}

# --- Templates: ---

def tpl_file(name):
    '''Build the full filename for template name.'''
    return os.path.join(abcDir, "%s.abc" % (name,))

def setTemplate(name, content):
    '''Set and save a template.'''
    abcTemplates[name] = content
    f = open(tpl_file(name), 'w')
    f.write(content)

def getTemplate(name, code):
    '''Load template by name and fill it with code'''
    if name is None:
        name="default"

    tpl = None

    if name not in abcTemplates:
        try:
            tpl = open(tpl_file(name)).read()
            if tpl and abcPattern in tpl:
                abcTemplates[name] = tpl
        except:
            if name == "default":
                tpl = abcTemplate
                setTemplate("default", tpl)
        finally:
            if name not in abcTemplates:
                raise IOError, "ABC Template %s not found or not valid." % (name,)

    # Replace one or more occurences of abcPattern

    codes = code.split(abcSplit)

    r = abcTemplates[name]

    for code in codes:
        r = r.replace(abcPattern, code, 1)

    return r

# --- GUI: ---

def templatefiles():
    '''Produce list of template files'''
    return [f for f in os.listdir(abcDir)
            if f.endswith(".abc")]

def addtemplate():
    '''Dialog to add a new template file'''
    name = getOnlyText("Please choose a name for your new ABC template:")

    if not abcNameRegexp.match(name):
        showInfo("Empty template name or invalid characters.")
        return

    if os.path.exists(tpl_file(name)):
        showInfo("A template with that name already exists.")

    setTemplate(name, abcTemplate)
    mw.addonManager.onEdit(tpl_file(name))

def abcMenu():
    '''Extend the addon menu with ABC template entries'''
    lm = mw.form.menuTools.addMenu(QIcon(os.path.join(abcDir,"abc.png")),"abc")

    a = QAction(_("Add template..."), mw)
    mw.connect(a, SIGNAL("triggered()"), addtemplate)
    lm.addAction(a)

    for file in templatefiles():
        m = lm.addMenu(os.path.splitext(file)[0])

        a = QAction(_("Edit..."), mw)
        p = os.path.join(abcDir, file)
        mw.connect(a, SIGNAL("triggered()"),
                   lambda p=p: mw.addonManager.onEdit(p))
        m.addAction(a)
        a = QAction(_("Delete..."), mw)
        mw.connect(a, SIGNAL("triggered()"),
                   lambda p=p: mw.addonManager.onRem(p))
        m.addAction(a)

# --- Functions: ---

def _abcFromHtml(abc):
    '''Convert entities and fix newlines'''

    abc = re.sub(r"<(br|div|p) */?>", "\n", abc)
    abc = stripHTML(abc)

    abc = abc.replace("&nbsp;", " ")

    for match in re.compile(r"&([a-zA-Z]+);").finditer(abc):
        if match.group(1) in entitydefs:
            abc = abc.replace(match.group(), entitydefs[match.group(1)])

    return abc

def _buildSnd(col, abc, fname):
    '''Build the sound MP3 file itself and add it to the media dir'''
    abcfile = open(abcFile, "w")
    abcfile.write(abc)
    abcfile.close()

    log = open(abcFile+".log", "w")

    if call(abc2midiCmd, stdout=log, stderr=log):
        return _errMsg("abc2midi")

    if call(timidityCmd, stdout=log, stderr=log):
        return _errMsg("timidity")

    if call(lameCmd, stdout=log, stderr=log):
        return _errMsg("lame")

    # add to media
    try:
        shutil.move(mp3File, os.path.join(col.media.dir(), fname))
    except:
        return _("Could not move MP3 file to media dir. No output?<br>")+_errMsg("move")

def _sndLink(col, template, abc):
    '''Build an [sound:<filename>] link for given ABC code'''

    # Finalize ABC source.
    abc = getTemplate(template, abc)
    abc = abc.encode("utf8")

    # Derive sound filename from source.
    fname = "abc-%s.mp3" % (checksum(abc),)
    link = "[sound:%s]" % (fname,)

    # Build sound if necessary.
    if os.path.exists(fname):
        return link
    else:
        # avoid errornous cards killing performance
        if fname in abcCache:
            return abcCache[fname]

        err = _buildSnd(col, abc, fname)
        if err:
            abcCache[fname] = err
            return err
        else:
            return link

def _errMsg(type):
    '''Error message, will be displayed in the card itself'''
    msg = (_("Error executing %s.") % type) + "<br>"
    try:
        log = open(abcFile+".log", "r").read()
        if log:
            msg += """<small><pre style="text-align: left">""" + cgi.escape(log) + "</pre></small>"
    except:
        msg += _("Have you installed abc2midi, timidity and lame?")
    return msg

# --- Hooks: ---

def mungeFields(fields, model, data, col):
    '''Parse ABC tags before they are displayed'''

    # Ignore duplicated mungeFields call for the answer side.
    if 'FrontSide' in fields:
        return fields

    for fld in model['flds']:
        field = fld['name']

        # check field name
        match = abcFieldRegexp.search(field)

        if match \
                and fields[field] != "(%s)" % (field,) \
                and fields[field] != "ankiflag":
            fields[field] = _sndLink(col, match.group(2), _abcFromHtml(fields[field]))

            # autofill field for web:
            sndfield = field.replace("abc", "abcsnd", 1)
            if sndfield in fields and fields[field] != fields[sndfield]:
                fields[sndfield] = fields[field]
                col.findReplace((data[1],), "^.*$", fields[field], regex=True, field=sndfield)
            continue

        # check field contents
        for match in abcRegexp.finditer(fields[field]):
            fields[field] = fields[field].replace(
                match.group(), _sndLink(col, match.group(2), _abcFromHtml(match.group(3)))
            )

    return fields

addHook("mungeFields", mungeFields)

def profileLoaded():
    '''Monkey patch the addon manager'''
    getTemplate(None, "") # creates default.abc if does not exist
    mw.addonManager.rebuildAddonsMenu = wrap(mw.addonManager.rebuildAddonsMenu, abcMenu)

addHook("profileLoaded", profileLoaded)

# --- End of file. ---
