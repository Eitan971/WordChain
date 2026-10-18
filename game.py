from nicegui import ui
import game_state
import concept_net as cn

def toast(message, duration=2000):
    ui.notify("<span style='font-size:40px'>"+message+"</span>", html=True, position='center', timeout=duration, 
              color='black', textColor='white', classes='big-toast')

def onWordEntered(e):
    word = e.sender.value
    e.sender.value = ""
    
    word = word.strip().lower()
    # Handle the entered word here
    #See if the word is related to the previous word
    r = cn.isRelatedByRelation(game_state.currentWord, word, game_state.currentRelation)

    debugPanel.refresh()
    
    if r is False:
        toast("Words are not related", 500)
        return

    # Did the user win?
    w = cn.isRelated(word, game_state.finalWord)
    if w:
        toast("Congratulations you won! :)", 10000)
        game_state.gameActive = False
        refreshUI()
        return

    # The word is valid, but the user did not win.
    # Therefore, we need to adapt everything.
    game_state.loseLife()
    if not game_state.isAlive():
        toast("Sorry, you lost! :(", 4000)
        game_state.gameActive = False
        refreshUI()
        return

    game_state.addToSequence(word)
    game_state.currentWord = word
    game_state.currentRelation, game_state.currentRelationDescription = cn.getNextRelation(word, game_state.currentRelation)
    refreshUI()



def hintPressed(e):
    if(game_state.hasHintsLeft()):
        hint = cn.getHint(game_state.currentWord, game_state.currentRelation, game_state.finalWord)
        toast(hint)
        game_state.usedHint()
        centerPanel.refresh()
    else:
        toast("You have no hints left :(")


def changeDebugMode(e):
    game_state.debugMode = e.value
    debugPanel.refresh()    

def refreshUI():
    centerPanel.refresh()
    debugPanel.refresh()
    bottomPanel.refresh()

def startNewGame():
    startWord, endWord = getInitialWords()
    if(difficultyRadio.value == "Easy"):
        diff = 0
    elif(difficultyRadio.value == "Medium"):
        diff = 1
    else:
        diff = 2

    style = None
    if styleInput.value:
        style = styleInput.value

    game_state.newGame(diff, startWord, endWord, imagesSwitch.value, style)

    game_state.currentRelation, game_state.currentRelationDescription = cn.getNextRelation(startWord, None)

    refreshUI()

def getInitialWords():
     startWord = cn.getInitialWord()
     endWord = cn.getLastWord(startWord)
     return startWord, endWord

@ui.refreshable
def centerPanel():
    if game_state.gameActive:
        with ui.row().classes('w-full justify-end gap-8'):
                ui.label(f"Turns: {game_state.turns}").classes('text-2xl font-bold')
                ui.label(f"Hints: {game_state.hints}").classes('text-2xl font-bold')
                ui.button("Hint").on_click(hintPressed)
        with ui.row().classes('items-center'):
            for item in game_state.sequence:
                with ui.card().tight():
                        if game_state.showImages:
                            ui.image(f"{item["image"]}").classes('w-50 h-50').bind_source_from(item, "image")
                        with ui.card_section().classes('w-full text-center'):
                                ui.label(f"{item["word"]}").classes('text-2xl font-bold')
                if item["id"] is not game_state.sequence[len(game_state.sequence)-1]["id"]:
                    ui.image("images/arrow.png").classes('w-30 h-30')
                if item["id"] is game_state.sequence[len(game_state.sequence)-2]["id"]:
                     ui.image("images/question.png").classes('w-50 h-50')
                     ui.image("images/arrow.png").classes('w-30 h-30')

@ui.refreshable
def bottomPanel():
    bottomFooter.set_value(game_state.gameActive)

    rel = "Next Relation: "
    if game_state.currentRelation:
        rel += game_state.currentRelation +": "+game_state.currentRelationDescription
    
    ui.label(rel).classes('text-xl font-bold')
    
    ui.input(placeholder='Enter next word').props('rounded outlined dense').classes('w-full text-xl font-bold').on('keydown.enter', onWordEntered).on('beforeinput', js_handler=r'''(e) => {if (e.data && /[^\p{L}-]/u.test(e.data)) e.preventDefault();}''')
        
@ui.refreshable
def debugPanel():
    debugDrawer.set_value(game_state.debugMode)
    if game_state.debugMode:
        ui.html(game_state.debugLog)

# Init ConceptNet
cn.init()


with ui.left_drawer(top_corner=True, bottom_corner=True).props('bordered width=200').style('background-color: #FFFFFF'):
    ui.image("images/logo.png")
    ui.label('Difficulty:')
    difficultyRadio = ui.radio(["Easy", "Medium", "Hard"],value="Easy")
    imagesSwitch = ui.switch("Show Images", value=False)
    styleInput = ui.input(placeholder='Style (optional)').props('rounded outlined dense').bind_visibility_from(imagesSwitch, 'value')   
    ui.button('Start Game!', on_click=startNewGame)
    ui.checkbox('Debug mode', value=True, on_change=changeDebugMode)

centerPanel()

with ui.right_drawer(bottom_corner=True).props('bordered') as debugDrawer:
    debugPanel() 

with ui.footer().style('background-color: lightblue; color: black').classes('h-30') as bottomFooter:
    bottomPanel()

ui.run()

