
import random
def Coin(author,priority,round):

    random.seed(author+priority+round)
    return random.randint(0,1)