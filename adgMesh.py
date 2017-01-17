'''
Created on 31/10/2014

@author: Alex Montes Barrios
'''

#
#  adjGraph
#
#  Created by Brad Miller on 2005-02-24.
#  Copyright (c) 2005 Brad Miller, David Ranum, Luther College. All rights reserved.
#

import sys
import os

class Graph:
    def __init__(self):
        self.vertices = {}
        self.numVertices = 0
        
    def addVertex(self,key):
        self.numVertices = self.numVertices + 1
        newVertex = Vertex(key)
        self.vertices[key] = newVertex
        return newVertex
    
    def getVertex(self,n):
        if n in self.vertices:
            return self.vertices[n]
        else:
            return None

    def __contains__(self,n):
        return n in self.vertices
    
    def addEdge(self,f,t,cost=0):
            if f not in self.vertices:
                nv = self.addVertex(f)
            if t not in self.vertices:
                nv = self.addVertex(t)
            self.vertices[f].addNeighbor(self.vertices[t],cost)
    
    def getVertices(self):
        return list(self.vertices.keys())
        
    def __iter__(self):
        return iter(self.vertices.values())
                
class Vertex:
    def __init__(self,num):
        self.id = num
        self.connectedTo = {}
        self.color = 'white'
        self.dist = sys.maxsize
        self.pred = None
        self.othSurces = []
        self.disc = 0
        self.fin = 0

    # def __lt__(self,o):
    #     return self.id < o.id

    def addSource(self, nbr):
        self.othSurces.append(nbr)
        
    def getSources(self):
        return self.othSurces
    
    def setSources(self, lista):
        self.othSurces = lista
    
    def addNeighbor(self,nbr,weight=0):
        self.connectedTo[nbr] = weight
        
    def setColor(self,color):
        self.color = color
        
    def setDistance(self,d):
        self.dist = d

    def setPred(self,p):
        self.pred = p

    def setDiscovery(self,dtime):
        self.disc = dtime
        
    def setFinish(self,ftime):
        self.fin = ftime
        
    def getFinish(self):
        return self.fin
        
    def getDiscovery(self):
        return self.disc
        
    def getPred(self):
        return self.pred
        
    def getDistance(self):
        return self.dist
        
    def getColor(self):
        return self.color
    
    def getConnections(self):
        return self.connectedTo.keys()
        
    def getWeight(self,nbr):
        return self.connectedTo[nbr]
                
    def __str__(self):
        return str(self.id) + ":color " + self.color + ":disc " + str(self.disc) + ":fin " + str(self.fin) + ":dist " + str(self.dist) + ":pred \n\t[" + str(self.pred)+ "]\n"
    
    def getId(self):
        return self.id


def buildGraph(wordFile):
    d = {}
    g = Graph()    
    wfile = open(wordFile,'r')
    # create buckets of words that differ by one letter
    for line in wfile:
        word = line[:-1]
        for i in range(len(word)):
            bucket = word[:i] + '_' + word[i+1:]
            if bucket in d:
                d[bucket].append(word)
            else:
                d[bucket] = [word]
    # add vertices and edges for words in the same bucket
    for bucket in d.keys():
        for word1 in d[bucket]:
            for word2 in d[bucket]:
                if word1 != word2:
                    g.addEdge(word1,word2)
    return g
    
class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

def bfs(g,start):
    start.setDistance(0)
    start.setPred(None)
    vertQueue = Queue()
    vertQueue.enqueue(start)
    while (vertQueue.size() > 0):
        currentVert = vertQueue.dequeue()
        for nbr in currentVert.getConnections():
            if (nbr.getColor() == 'white'):
                nbr.setColor('gray')
                nbr.setDistance(currentVert.getDistance() + 1)
                nbr.setPred(currentVert)
                vertQueue.enqueue(nbr)
            currentVert.setColor('black') 
    
    
def traverse(y):
    x = y
    while (x.getPred()):
        print(x.getId())
        x = x.getPred()
    print(x.getId())


def printTree(node, indent):
    print indent*'    ' + node.getId()
    for child in node.getConnections():
        if node.getWeight(child) == 10:  
            printTree(child, indent + 1)
            for inLnk in child.getSources():
                print (indent + 1)*'    ' + '<=' + inLnk.getId()
        else:
            print indent*'    ' + '=>' + child.getId()


if __name__ == '__main__':
#     wordgraph = buildGraph("fourletterwords.txt")
#     bfs(wordgraph, wordgraph.getVertex('FOOL'))
#     traverse(wordgraph.getVertex('SAGE'))

    import json
    name = "vodly.pck"
    with open(name,'rb') as f:
        treeData = json.loads(f.readline())[1]
        settings = json.loads(f.readline())
        modifiedCode = json.loads(f.readline())

    g = Graph()
    toProcess = ['rootmenu']
    while toProcess:
        actNode = toProcess.pop(0)
        frstChild = treeData[actNode].get('down', None)
        while frstChild:
            if treeData[frstChild].get('type') == 'link':
                weight = 1
                toNode = treeData[frstChild].get('name')
            else:
                weight = 0
                toNode = frstChild
                toProcess.append(frstChild)
            g.addEdge(actNode, toNode, weight)
            frstChild = treeData[frstChild].get('sibling', None)

    toProcess = ['media']
    while toProcess:
        actNode = toProcess.pop(0)
        frstChild = treeData[actNode].get('down', None)
        while frstChild:
            if treeData[frstChild].get('type') != 'link':
                weight = 0
                toNode = frstChild
                toProcess.append(frstChild)
                g.addEdge(toNode, actNode, weight)
            frstChild = treeData[frstChild].get('sibling', None)

    toRootMenu = [vrtx for vrtx in treeData if not treeData[vrtx].get('down', None) and treeData[vrtx].get('type')=='thread']
    for key in toRootMenu:
        g.addEdge('rootmenu', key, 1)

#     actNode = g.getVertex('rootmenu')
#     toProcess = [actNode]
#     k = 0
#     while k <= len(toProcess) - 1:
#         actNode = toProcess[k]
#         for key in actNode.getConnections():
#             if key not in toProcess:
#                 toProcess.append(key)
#                 key.setPred(actNode.getId())
#         k += 1

    bfs(g, g.getVertex('rootmenu'))

    for vertx in g: vertx.setSources([])
    actNode = g.getVertex('rootmenu')
    toProcess = [actNode]
    k = 0
    while k <= len(toProcess) - 1:
        actNode = toProcess[k]
        for key in actNode.getConnections():
            if key not in toProcess:
                toProcess.append(key)
                actNode.connectedTo[key] = 10
            else:
                actNode.connectedTo[key] = 20
                key.addSource(actNode)
        k += 1

    actNode = g.getVertex('rootmenu')
    printTree(actNode, 0)
    print 3*'\n'
    
    for key in sorted(g.getVertices()):
        vertx = g.getVertex(key) 
        print vertx.getId(), vertx.getPred(), sorted([(inVtx.getId(),value) for inVtx, value in vertx.connectedTo.items()])
        