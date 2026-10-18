import os
import random
import jev

import game_state as gs
import conceptnet_lite
from collections import defaultdict
from dotenv import load_dotenv
from openai import OpenAI

VALID_RELATIONS = {
    "antonym": "Words with opposite meanings.",
    "capable_of": "Something the thing can typically do.",
    "causes": "One commonly causes the other.",
    "has_first_subevent": "The other is the first step of the event.",
    "has_last_subevent": "The other is the last step of the event.",
    "has_subevent": "The other happens as part of the first event.",
    "is_a": "One is a kind of the other (e.g. a cat is an animal).",
    "manner_of": "One is a specific way of doing the other.",
    "motivated_by_goal": "The reason or goal behind doing the thing.",
    "related_to": "Loosely connected in some way (a vague, general association).",
    "synonym": "Words with very similar meanings.",
    "at_location": "Where the thing is typically found.",
    "causes_desire": "The thing makes someone want the other.",
    "part_of": "One is a part of the other.",
    "used_for": "What the thing is used for."
}

FIRST_WORDS_COUNT = 1000
FIRST_WORDS_FILE = "data/first_words.txt"

MIN_RELATION_ITEMS = 5
MAX_RELATION_CANDIDATES = 3

def init():
    gs.log("Initializing ConceptNet...")
    conceptnet_lite.connect("data/conceptnet.db")
    gs.log("->ConceptNet initialized.")


def isEnglish(concept):
    language = concept.language
    return language is not None and language.name == "en"

def getRelations(word):
    gs.log(f"Getting relations for word '{word}'...")
    try:
        relations = defaultdict(dict)
        w = word.strip().lower().replace(" ", "_")
        concepts = conceptnet_lite.Label.get(text=w, language="en"). concepts

        for concept in concepts:
            for edge in concept.edges_out:
                if isEnglish(edge.end) and edge.relation.name in VALID_RELATIONS and "_" not in edge.end.text:
                    relations[edge.relation.name][edge.end.text] = (edge.etc.get("weight", 1.0), "→")
            for edge in concept.edges_in:
                if isEnglish(edge.start) and edge.relation.name in VALID_RELATIONS and "_" not in edge.start.text:
                    relations[edge.relation.name][edge.start.text] = (edge.etc.get("weight", 1.0), "←")

       # for relation, targets in relations.items():
       #     gs.log(f"  - {relation} ({len(targets)} matches)")

        return relations
    except conceptnet_lite.Label.DoesNotExist:
        return None
    except Exception as e:
        gs.log(f"->Error getting relations for word '{word}': {e}")
        return None

def printRelations(relations):
    if relations is None:
        print("No relations found.")
        return
    for relation, targets in relations.items():
        print(f"{relation} ({VALID_RELATIONS[relation]}):")
        for target, (weight, direction) in targets.items():
            print(f"  {direction} {target} (weight: {weight})")

def getNextRelation(word, lastRelation):
    gs.log(f"Getting next relation for word '{word}' after last relation '{lastRelation}'...")
    relations = getRelations(word)

    # Create a list of candidate relations that have at least MIN_RELATION_ITEMS
    candidates = []
    for relation, targets in relations.items():
        if len(targets) >= MIN_RELATION_ITEMS and lastRelation != relation:
            candidates.append(relation)

    gs.log(f"->Candidates: {candidates}")

    # If no candidates, just return the first relation in relations
    if not candidates:
        return list(relations.keys())[0]

    chosenRelation = random.choice(candidates[:MAX_RELATION_CANDIDATES]) if candidates else None
    gs.log(f"->Chosen relation: {chosenRelation}")

    # Return the chosen relation and its description from VALID_RELATIONS
    return chosenRelation, VALID_RELATIONS.get(chosenRelation)

def isRelatedByRelation(currentWord, userWord, relation):
    gs.log(f"Checking if '{currentWord}' is related to '{userWord}' by '{relation}' using ConceptNet...")
    
    # First checking if userWord exists in ConceptNet
    if getRelations(userWord) is None:
        return False

    relations = getRelations(currentWord) or {}

    # Check if userWord is in relations of currentWord and assign the result to a boolean
    isRelated = False
    if userWord in relations.get(relation, {}):
        isRelated = userWord in relations.get(relation, {})

    if isRelated:
        gs.log(f"->Relation Found!")
        return True
    else:
        gs.log(f"->Relation Not Found. Fallback to JEV.")
        relationDescription = VALID_RELATIONS.get(relation)

        jevRelated = jev.areRelated(currentWord, userWord, relation, relationDescription)

        gs.log(f"->JEV Relation Result: {jevRelated}")

        return jevRelated

# Check if the user has won by determining if userWord has a direct relationship to finalWord through any of the VALID_RELATIONS
def isRelated(userWord, finalWord):
    gs.log(f"Checking if '{userWord}' is related to '{finalWord}' using ConceptNet...")
    relations = getRelations(userWord)
    if relations is None:
        return False

    for relation in relations:
        if finalWord in relations.get(relation, {}):
            gs.log(f"->Relation Found in ConceptNet: {relation}")
            return True

    gs.log(f"->No relation found in ConceptNet. Falling back to JEV.")
    return jev.areRelated(userWord, finalWord)

# For all words that connect to userWord with a specific relation, run a similarity test with finalWord and return the most similar.
def getHint(userWord, relation, finalWord):
    gs.log(f"Getting hint for '{userWord}' with relation '{relation}' towards '{finalWord}'...")

    load_dotenv()
    client = OpenAI(api_key=os.environ["OPENAI_API"])

    response = client.responses.create(
        model="gpt-6-luna",
        input = f"Give exactly one common English word that is this relation: {relation} to this word {userWord}, and brings the user somewhat closer to this word {finalWord}, but not too close!. Relationship Descriptions: {VALID_RELATIONS}"
    )

    reply = response.output_text
    return reply

    

    

# Create a list of 1000 words that has the most connections in ConceptNet in the valid relations that we want and save into a file 
# I did not create this function (it was created by AI)
def createListOfFirstWords():
    gs.log(f"Creating list of {FIRST_WORDS_COUNT} first words...")
    database = conceptnet_lite.db.db

    names = list(VALID_RELATIONS)
    placeholders = ",".join("?" * len(names))
    relationIds = [row[0] for row in database.execute_sql(
        f"SELECT id FROM relation WHERE name IN ({placeholders})", names)]

    # Map every English concept id to its text
    englishConcepts = {}
    for conceptId, text in database.execute_sql(
            "SELECT c.id, l.text FROM concept c "
            "JOIN label l ON c.label_id = l.id "
            "JOIN language g ON l.language_id = g.id WHERE g.name = 'en'"):
        englishConcepts[conceptId] = text
    gs.log(f"    {len(englishConcepts)} English concepts loaded.")

    # Same counting rules as getRelations: unique (relation, other word) pairs, other word is a single word
    connections = defaultdict(set)
    idList = ",".join(str(i) for i in relationIds)
    for relationId, startId, endId in database.execute_sql(
            f"SELECT relation_id, start_id, end_id FROM edge WHERE relation_id IN ({idList})"):
        start = englishConcepts.get(startId)
        end = englishConcepts.get(endId)
        if start is None or end is None or start == end:
            continue
        if "_" not in end:
            connections[start].add((relationId, end))
        if "_" not in start:
            connections[end].add((relationId, start))

    candidates = [(len(links), word) for word, links in connections.items() if word.isalpha()]
    candidates.sort(key=lambda item: (-item[0], item[1]))
    words = [word for _, word in candidates[:FIRST_WORDS_COUNT]]

    os.makedirs(os.path.dirname(FIRST_WORDS_FILE), exist_ok=True)
    with open(FIRST_WORDS_FILE, "w") as f:
        f.write("\n".join(words) + "\n")

    gs.log(f"    Saved {len(words)} words to {FIRST_WORDS_FILE}.")
    return words


# returns a random initial word from the list of first words
def getInitialWord():
    with open(FIRST_WORDS_FILE, "r") as f:
        words = [line.strip() for line in f.readlines()]
    return random.choice(words)

def getLastWord(initialWord):
    with open(FIRST_WORDS_FILE, "r") as f:
        words = [line.strip() for line in f.readlines()]
    while True:
        wordChosen = random.choice(words)
        if wordChosen != initialWord:
            return random.choice(words)
















