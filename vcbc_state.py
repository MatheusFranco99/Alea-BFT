
class ReadyState:

    def __init__(self):
        self.readys = {}
    
    def add(self,priority,id):
        if priority not in self.readys:
            self.readys[priority] = set()
        
        self.readys[priority].add(id)
    
    def getLen(self,priority):
        if priority not in self.readys:
            return 0
        return len(self.readys[priority])


class VCBCState:

    def __init__(self,nodes_ids):
        self.num_nodes = len(nodes_ids)
        self.data = {id: {} for id in nodes_ids}
        
    
    def add(self,id,data,priority):
        if priority in self.data[id]:
            print("VCBCState: Trying to add to already existing priority")
        else:
            self.data[id][priority] = data
    
    def has(self,id,priority):
        return priority in self.data[id]

    def get(self,id,priority):
        if priority not in self.data[id]:
            return None
        else:
            return self.data[id][priority]
    
    def peek(self,id):
        keys = self.data[id].keys()
        if len(keys) == 0:
            return None
        min_key = min(keys)
        return self.data[id][min_key]

    def pop(self,id):
        keys = self.data[id].keys()
        if len(keys) == 0:
            return None
        min_key = min(keys)
        data = self.data[id][min_key]
        del self.data[id][min_key]
        return data

    def remove(self,id,priority):
        if priority in self.data[id]:
            del self.data[id][priority]

        
