import numpy as np
from model2vec import StaticModel

def init():
    global m2v
    m2v = StaticModel.from_pretrained("minishlab/potion-base-8M")

def similarity(word1, word2):
   a, b = m2v.encode([word1, word2])
   return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

#init()
#print(similarity("castle", "princess"))

