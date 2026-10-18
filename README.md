# WordChain

A word game inspired by Linked (https://time.com/games/linked), but with much more flexibility and features.

The game gives you a start word and an end word, and you need to figure out a way to get from one to the other. The twist is that, for each step, you are limited to only the type of relation assigned for that turn.

ConceptNet (https://conceptnet.io) is used to:
- Find all relations that a word has.
- Determine the first and last word.
- Determine the next turn's relation.
- Find out if two words are related (used to determine if an entered word is correct, and also to determine if the user has won).

If a relation between two words cannot be found using ConceptNet, the game uses Jev (http://typesafe.ai/blog/introducing-system-one-models-and-jev) to determine if there is one. If the query returns a 50% or higher probability that there is, the word is approved.

The OpenAI API is utilized to send a prompt to GPT-6 Luna to provide the user with a hint based on their current word, the final word, and the current relation. This is done when the user clicks the hint button. 

Finally, the game optionally uses Recraft (recraft.ai) to generate images for all words, with an optional style. The model used (Recraft V4.1 Flash) is the fastest image generation model I found at the time this project was made.


