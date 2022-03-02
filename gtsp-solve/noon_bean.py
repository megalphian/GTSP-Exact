# Noon-Bean transformation for GTSP to TSP
# Adapted from the MATLAB repository here: 
# Neil (2022). Noon-Bean Transformation (https://www.mathworks.com/matlabcentral/fileexchange/44467-noon-bean-transformation), MATLAB Central File Exchange.

import numpy as np

def gtsp_to_tsp(gtspAdjMatrix, setMap):

    atspAdjMatrix = np.ones(np.shape(gtspAdjMatrix)) * -1
    adjMatrixCostCalcs = gtspAdjMatrix*0

    # intra-cluster arcs
    numSets = setMap.max() + 1
    
    for i in range(numSets):

        # intra-cluster arcs
        indexes = np.where(setMap == i)[0]
        
        if(len(indexes) > 1):
            
            for j in range(len(indexes)-1):
                atspAdjMatrix[indexes[j],indexes[j+1]] = 0
            atspAdjMatrix[indexes[-1],indexes[0]] = 0


        # inter-cluster arc switching
        for j in range(1,len(indexes)):
            for k in range(len(setMap)):
                if(setMap[indexes[j]] != setMap[k]):
                    if(gtspAdjMatrix[indexes[j],k] != 0):
                        atspAdjMatrix[indexes[j-1],k] = gtspAdjMatrix[indexes[j],k]
                        adjMatrixCostCalcs[indexes[j-1],k] = gtspAdjMatrix[indexes[j],k]

        for k in range(len(setMap)):
            if(setMap[indexes[0]] != setMap[k]):
                if(gtspAdjMatrix[indexes[0],k] != 0):
                    atspAdjMatrix[indexes[-1],k] = gtspAdjMatrix[indexes[0],k]
                
                    adjMatrixCostCalcs[indexes[-1],k] = gtspAdjMatrix[indexes[0],k]
                
    # using max instead of sum. slight difference from original Noon-Bean
    #totalcost = sum(sum(adjMatrixCostCalcs))
    maxCost = adjMatrixCostCalcs.max()
    beta = 2*maxCost
    for i in range(len(setMap)):
        for j in range(len(setMap)):
            
            if(atspAdjMatrix[i,j] != 0 and atspAdjMatrix[i,j] != -1):
                
                # %------------ NOTE -------------------------------------
                # % factor of a 1000 added. Ok since max is used earlier
                # % this value can be changed around
                # % potential bug: values become too large for TSP solvers. 
                # %-------------------------------------------------------
                
                atspAdjMatrix[i,j] = (atspAdjMatrix[i,j] + beta) * 100
                adjMatrixCostCalcs[i,j] = adjMatrixCostCalcs[i,j] + beta

    totalcost = adjMatrixCostCalcs.sum()
    beta2 = 5*totalcost
    for i in range(len(setMap)):
        for j in range(len(setMap)):
            if(atspAdjMatrix[i,j] == -1):
                atspAdjMatrix[i,j] = beta2

    return atspAdjMatrix
