

# for each author:
#   - current priority
#   - map: priority -> executions
#   
#   execution:
#   - round execution:
#       - init list
#       - sent init
#       - aux lst
#       - sent aux
#       - conf lst
#       - sent conf
#       - finish lst
#       - sent finish

class ABARound:

    def __init__(self):
        self.init = {}
        self.sentInit = [False,False]
        self.aux = {}
        self.sentAux = [False,False]
        self.conf = {}
        self.sentConf = False

    def addInit(self,vote,sender):
        if sender in self.init:
            return
        self.init[sender] = vote
    
    def lenInit(self,vote):
        ans = 0
        for v in self.init.values():
            if v == vote:
                ans += 1
        return ans

    def setSentInit(self,vote):
        if vote in [0,1]:
            self.sentInit[vote] = True

    def hasSentInit(self,vote):
        if vote in [0,1]:
            return self.sentInit[vote]

    def addAux(self,vote,sender):
        if sender in self.aux:
            return
        self.aux[sender] = vote
    
    def lenAux(self):
        return len(self.aux.values())

    def setSentAux(self,vote):
        if vote in [0,1]:
            self.sentAux[vote] = True

    def hasSentAux(self,vote):
        if vote in [0,1]:
            return self.sentAux[vote]

    def addConf(self,votes,sender):
        if sender in self.conf:
            return
        self.conf[sender] = votes
    
    def lenConf(self):
        return len(self.conf.values())

    def setSentConf(self):
        self.sentConf = True

    def hasSentConf(self):
        return self.sentConf
    
    def getConfValues(self):
        return list(set(self.aux.values()))






class ABA:
    def __init__(self):
        self.abarounds = {0:ABARound()}
        self.round = 0
        self.finish = {}
        self.sentFinish = [False,False]
    
    def initRound(self,round):
        if round not in self.abarounds:
            self.abarounds[round] = ABARound()
    
    def addRound(self,round):
        if round not in self.abarounds:
            self.abarounds[round] = ABARound()

    def __iter__(self):
        self.n = 0
        self.temp_keys = self.abarounds.keys()
        return self

    def __next__(self):
        if self.n < len(self.temp_keys):
            result = self.abarounds[self.temp_keys[self.n]]
            self.n += 1
            return result
        else:
            raise StopIteration

    def __getitem__(self, index):
        return self.abarounds[index]



    def addFinish(self,vote,sender):
        if sender in self.finish:
            return
        self.finish[sender] = vote
    
    def lenFinish(self,vote):
        ans = 0
        for v in self.finish.values():
            if v == vote:
                ans += 1
        return ans

    def setSentFinish(self,vote):
        if vote in [0,1]:
            self.sentFinish[vote] = True

    def hasSentFinish(self,vote):
        if vote in [0,1]:
            return self.sentFinish[vote]

class ABAState:

    def __init__(self,nodes_ids):
        self.abas = {id:{} for id in nodes_ids}
        self.priority = {id:0 for id in nodes_ids}

        for id in nodes_ids:
            self.init(id,0)
        
        self.decided = {id:{} for id in nodes_ids}
    
    def init(self,id,priority):
        self.abas[id][priority] = ABA()

    
    def currentPriority(self,author):
        return self.priority[author]
        
    def currentRound(self,author,priority):
        if priority not in self.abas[author]:
            self.abas[author][priority] = ABA()
        return self.abas[author][priority].round

        
    def setRound(self,author,priority,round):
        if priority not in self.abas[author]:
            self.abas[author][priority] = ABA()
        self.abas[author][priority].round = round
        
    def setDecided(self,author,priority,vote):
        if priority not in self.decided[author]:
            self.decided[author][priority] = vote
    
    def isDecided(self,author,priority):
        return priority in self.decided[author]


        
    def setPriority(self,author,priority):
        self.priority[author] = priority

    def setupPriority(self,author,priority):
        if priority not in self.abas[author]:
            self.abas[author][priority] = ABA()
    
    def setupRound(self,author,priority,round):
        self.setupPriority(author,priority)

        self.abas[author][priority].initRound(round)

    # ------------------------------------------    

    def addInit(self,author,priority,round,vote,sender):
        self.setupRound(author,priority,round)
        self.abas[author][priority][round].addInit(vote,sender)
        
    def lenInit(self,author,priority,round,vote):
        self.setupRound(author,priority,round)
        return self.abas[author][priority][round].lenInit(vote)
        
    def setSentInit(self,author,priority,round,vote):
        self.setupRound(author,priority,round)
        return self.abas[author][priority][round].setSentInit(vote)
        
    def hasSentInit(self,author,priority,round,vote):
        self.setupRound(author,priority,round)
        return self.abas[author][priority][round].hasSentInit(vote)
    
    # ------------------------------------------ 

    def hasSentAux(self,author,priority,round,vote):
        self.setupRound(author,priority,round)
        return self.abas[author][priority][round].hasSentAux(vote)
        
        
    def setSentAux(self,author,priority,round,vote):
        self.setupRound(author,priority,round)
        self.abas[author][priority][round].setSentAux(vote)

        
    def lenAux(self,author,priority,round):
        self.setupRound(author,priority,round)
        return self.abas[author][priority][round].lenAux()
        
    def addAux(self,author,priority,round,vote,sender):
        self.setupRound(author,priority,round)
        self.abas[author][priority][round].addAux(vote,sender)
        
    
    # ------------------------------------------ 
    def hasSentConf(self,author,priority,round):
        self.setupRound(author,priority,round)
        return self.abas[author][priority][round].hasSentConf()
        
    def getConfValues(self,author,priority,round):
        self.setupRound(author,priority,round)
        return self.abas[author][priority][round].getConfValues()
        
    def setSentConf(self,author,priority,round):
        self.setupRound(author,priority,round)
        return self.abas[author][priority][round].setSentConf()
        
    def addConf(self,author,priority,round,votes,sender):
        self.setupRound(author,priority,round)
        self.abas[author][priority][round].addConf(votes,sender)
        
    def lenConf(self,author,priority,round):
        self.setupRound(author,priority,round)
        return self.abas[author][priority][round].lenConf()

    
    # ------------------------------------------ 
    def setSentFinish(self,author,priority,vote):
        return self.abas[author][priority].setSentFinish(vote)
        
    def addFinish(self,author,priority,vote,sender):
        self.abas[author][priority].addFinish(vote,sender)
        
    def lenFinish(self,author,priority,vote):
        return self.abas[author][priority].lenFinish(vote)
        
    def hasSentFinish(self,author,priority,value):
        return self.abas[author][priority].hasSentFinish(value)