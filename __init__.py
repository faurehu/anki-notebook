import os
from aqt import mw
from anki.hooks import addHook
from anki.importing import TextImporter

config = mw.addonManager.getConfig(__name__)

FILE_EXTENSION = ".anbk"
CLOZE_LEADING_INDICATOR = "C:"
notes = {}

def serialiseFile(path, deckName):
    with open(path) as ins:
        cloze = []
        basic = []
        for line in ins:
            if line[:1] == "#":
                continue
            if line[:2] == CLOZE_LEADING_INDICATOR:
                c = line[2:]
                if c[:1] == " ":
                    c = c[1:]
                cloze.append(c)
                continue
            basic.append(line)

    notes[deckName] = {
        'cloze': cloze,
        'basic': basic
    }

def traverseDir(path, nodes):
    for filename in os.listdir(path):
        filePath = path + "/" + filename
        isDir = os.path.isdir(filePath)
        if isDir:
            traverseDir(filePath, nodes + [filename])
        elif filename.endswith(FILE_EXTENSION):
            deckName = "AnkiNotebook::"
            if len(nodes) > 0:
                deckName += ("::").join(nodes) + "::"
            deckName += filename[:-5]
            serialiseFile(filePath, deckName)

def importFile(deckId, notes, noteType):
    if len(notes) == 0:
        return


    with open(u"tmp.txt", "w") as f:
        for item in notes:
            f.write("%s\n" % item)

    m = mw.col.models.byName(noteType)
    deck = mw.col.decks.get(deckId)
    deck['mid'] = m['id']
    m['did'] = deckId
    mw.col.decks.save(deck)
    mw.col.models.save(m)


    ti = TextImporter(mw.col, u"tmp.txt")
    ti.delimiter = ","
    ti.initMapping()
    ti.run()

    os.remove(u"tmp.txt")

def main():
    traverseDir(config["notebookPath"], [])
    for key in notes:
        did = mw.col.decks.id(key)
        mw.col.decks.select(did)
        importFile(did, notes[key]["basic"], "Basic (optional reversed card)")
        importFile(did, notes[key]["cloze"], "Cloze")
    mw.reset()

addHook("profileLoaded", main)

