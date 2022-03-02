import gurobipy as gp
from gurobipy import GRB, abs_

from itertools import combinations

import numpy as np

# Callback - use lazy constraints to eliminate sub-tours

def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        # make a list of edges selected in the solution
        vals = model.cbGetSolution(model._vars)
        selected = gp.tuplelist((i, j) for i, j in model._vars.keys()
                            if vals[i, j] > 0.5)
        # find the shortest cycle in the selected edge list
        tour = TSPSolver.subtour(selected)
        if len(tour) < len(TSPSolver.nodes):
            # add subtour elimination constr. for every pair of cities in subtour
            model.cbLazy(gp.quicksum(model._vars[i, j] + model._vars[j, i] for i, j in combinations(tour, 2))
                        <= len(tour)-1)

class TSPSolver:

    nodes = None

    # Given a tuplelist of edges, find the shortest subtour

    @staticmethod
    def subtour(edges):
        unvisited = TSPSolver.nodes[:]
        cycle = TSPSolver.nodes[:] # Dummy - guaranteed to be replaced
        while unvisited:  # true if list is non-empty
            thiscycle = []
            neighbors = unvisited
            while neighbors:
                current = neighbors[0]
                thiscycle.append(current)
                unvisited.remove(current)
                neighbors = [j for _, j in edges.select(current, '*')
                            if j in unvisited]
            if len(thiscycle) <= len(cycle):
                cycle = thiscycle # New shortest subtour
        return cycle

    def setup_graph(self, tsp_adj_mat):

        var_dict = dict()
        node_len = np.shape(tsp_adj_mat)[0]
        TSPSolver.nodes = list(range(node_len))
        
        for i in TSPSolver.nodes:
            for j in TSPSolver.nodes:
                if(tsp_adj_mat[i,j] != -1):
                    var_dict[(i,j)] = tsp_adj_mat[i,j]

        return var_dict

    def solve_exact_tsp(self, tsp_adj_mat):

        m = gp.Model()

        tsp_graph = self.setup_graph(tsp_adj_mat)

        vars = m.addVars(tsp_graph.keys(), obj=tsp_graph, vtype=GRB.BINARY, name='x')

        # Constraints: one entry edge and one exit edge
        cons1 = m.addConstrs(vars.sum(c, '*') == 1 for c in TSPSolver.nodes)
        cons2 = m.addConstrs(vars.sum('*', c) == 1 for c in TSPSolver.nodes)

        m._vars = vars
        m.Params.lazyConstraints = 1
        m.optimize(subtourelim)

        vals = m.getAttr('x', vars)
        selected = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)

        tour = TSPSolver.subtour(selected)
        assert len(tour) == len(TSPSolver.nodes)

        return tour

