import uuid
import recraft
from nicegui import run, background_tasks

turns = 0
hints = 0
difficulty = 0 #0 = easy, 1 = medium, 2 = hard
gameActive = False
sequence = []
debugMode = True
debugLog = ""
currentWord=None
currentRelation=None
currentRelationDescription = None
finalWord=None
showImages=False
imageStyle=None

def newGame(diff, startWord, endWord, sImages, iStyle):
    global turns, hints, difficulty, gameActive, debugLog, sequence, currentWord, currentRelation, currentRelationDescription, finalWord, showImages, imageStyle
    if diff == 0:
        turns = 10
        hints = 3
    elif diff == 1:
        turns = 8
        hints = 2
    else:
        turns = 6
        hints = 1
    difficulty = diff
    sequence = []
    gameActive = True
    currentWord = startWord
    finalWord = endWord
    showImages = sImages
    imageStyle = iStyle
    currentRelation = None
    currentRelationDescription = None
    startUuid = addToSequence(startWord)
    endUuid = addToSequence(endWord)
    debugLog = ""
    log ("Game Started...")
    return startUuid, endUuid

def log(message):
    global debugLog
    debugLog += message + "<br>"

def isAlive():
    return (turns > 0)

def hasHintsLeft():
    return (hints > 0)

def loseLife():
    global turns, gameActive
    turns-=1
    if turns == 0:
        gameActive = False

def usedHint():
    global hints
    hints-=1

async def loadImage(item):
    fileName = f"{item['id']}.png"
    if await run.io_bound(recraft.getImage, item["word"], imageStyle, fileName):
        item["image"] = f"recraftimages/{fileName}"


def addToSequence(word):
    u = str(uuid.uuid4())
    item={"id": u, "word": word, "image": "images/placeholdernew.png"}
    if len(sequence) < 2:
        sequence.append(item)
    else:
        sequence.insert(len(sequence)-1, item)

    if showImages:
        background_tasks.create(loadImage(item))
    return u