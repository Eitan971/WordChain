import os
from tkinter import NO
import httpx
from dotenv import load_dotenv
import game_state as gs

load_dotenv()

JEV_URL = "https://api.typesafe.ai/v1/systemone"
JEV_MODEL = "jev-latest"
TRUTH_THRESHOLD = 0.5

def areRelated(currentWord, userWord, relation = None, relationDescription = None):

    if relation is None:
        gs.log(f"JEV: Checking if '{currentWord}' is related to '{userWord}'") #Add Closely if it is too vague
    else:
        gs.log(f"JEV: Checking if '{currentWord}' is related to '{userWord}' by '{relation}'")

    if relation is None:
        instructions = (f"Is the word {currentWord} CLOSELY related to the word {userWord}?")
    else:
        instructions = (
            f"Is the word {currentWord} related to the word {userWord} "
            f"in the following way: {relation} ({relationDescription})?"
        )

    response = httpx.post(
        JEV_URL,
        headers={"Authorization": f"Bearer {os.environ['JEV_API']}"},
        json={
            "model": JEV_MODEL,
            "state": {"current_word": currentWord, "user_word": userWord},
            "questions": {"related": {"type": "noul", "instructions": instructions}},
        },
        timeout=30,
    )

    # If no Internet, return No 
    if response.status_code == 0:
        return False

    response.raise_for_status()
    truth = response.json()["answers"]["related"]["noul"]

    gs.log(f"    Truth value for relation is {truth}")
    # Log if it meet current truth threshold
    if truth >= TRUTH_THRESHOLD:
        gs.log(f"    Relation meets the truth threshold.")
    else:
        gs.log(f"    Relation does not meet the truth threshold.")

    return True if truth >= TRUTH_THRESHOLD else False


#x = areRelated("sweating", "exercising", "causes", "One commonly causes the other.")
#print(x)
