
from itertools import chain, combinations
from aimacode.planning import Action
from aimacode.utils import expr

from layers import BaseActionLayer, BaseLiteralLayer, makeNoOp, make_node

class ActionLayer(BaseActionLayer):

    def _inconsistent_effects(self, actionA, actionB):
        """ Return True if an effect of one action negates an effect of the other

        See Also
        --------
        layers.ActionNode
        """
        
        """        
        Inconsistent effects: one action negates an effect of the other. For example Eat(Cake)
        and the persistence of Have(Cake) have inconsistent effects because they disagree on
        the effect Have(Cake).        
        """
        # TODO: implement this function
        #raise NotImplementedError
        
        for effectA in actionA.effects:
            for effectB in actionB.effects:
                if effectA == ~effectB:
                    return True
        return False        


    def _interference(self, actionA, actionB):
        """ Return True if the effects of either action negate the preconditions of the other
        
        See Also
        --------
        layers.ActionNode
        """
        """
        Interference: one of the effects of one action is the negation of a precondition of the
        other. For example Eat(Cake) interferes with the persistence of Have(Cake) by negating
        its precondition.
        """
        
        # TODO: implement this function
        #raise NotImplementedError
        for effect in actionA.effects:
            for precondition in actionB.preconditions:
                if effect == ~precondition:
                    return True
        for effect in actionB.effects:
            for precondition in actionA.preconditions:
                if effect == ~precondition:
                    return True                    
        return False
        
    def _competing_needs(self, actionA, actionB):
        """ Return True if the preconditions of the actions are all pairwise mutex in the
            parent layer
        
        See Also
        --------
        layers.ActionNode
        layers.BaseLayer.parent_layer
        """
        """
        Competing needs: one of the preconditions of one action is mutually exclusive with a
        precondition of the other. For example, Bake(Cake) and Eat(Cake) are mutex because
        they compete on the value of the Have(Cake) precondition.
        
         

        """
        for preconditionA in actionA.preconditions:
            for preconditionB in actionB.preconditions:
                if self.parent_layer.is_mutex(preconditionA, preconditionB):
                    return True
        return False

class LiteralLayer(BaseLiteralLayer):

    def _inconsistent_support(self, literalA, literalB):
        """ Return True if all ways to achieve both literals are pairwise mutex in the parent
        layer

        See Also
        --------
        layers.BaseLayer.parent_layer
        """
        """
        Inconsistent support: At(Spare, Axle) is mutex with At(Flat, Axle) in S2 because the
        only way of achieving At(Spare, Axle) is by PutOn(Spare, Axle), and that is mutex
        with the persistence action that is the only way of achieving At(Flat, Axle). Thus, the
        mutex relations detect the immediate conflict that arises from trying to put two objects
        in the same place at the same time.
        
        A mutex relation holds between two literals at the same level if one is the negation of
        the other
        or if each possible pair of actions that could achieve the two literals is mutually
        exclusive.
        This condition is called inconsistent support. For example, Have(Cake) and Eaten(Cake)
        are mutex in S1 because the only way of achieving Have(Cake), the persistence action, is
        mutex with the only way of achieving Eaten(Cake), namely Eat(Cake). In S2 the two
        literals are not mutex because there are new ways of achieving them, such as Bake(Cake)
        and the persistence of Eaten(Cake), that are not mutex.
        """
        literalsA = self.parents[literalA] 
        literalsB = self.parents[literalB]
        # TODO: implement this function
        #raise NotImplementedError
        for literalA in literalsA:
           for literalB in literalsB:
               if not self.parent_layer.is_mutex(literalA, literalB):
                   return False
        return True        

    def _negation(self, literalA, literalB):
        """ Return True if two literals are negations of each other """
        # TODO: implement this function
        #raise NotImplementedError   
        #return ((literalA == ~literalB) and (literalB == ~literalA))
        return literalA == ~literalB
    
    
class PlanningGraph:
    def __init__(self, problem, state, serialize=True, ignore_mutexes=False):
        """
        Parameters
        ----------
        problem : PlanningProblem
            An instance of the PlanningProblem class

        state : tuple(bool)
            An ordered sequence of True/False values indicating the literal value
            of the corresponding fluent in problem.state_map

        serialize : bool
            Flag indicating whether to serialize non-persistence actions. Actions
            should NOT be serialized for regression search (e.g., GraphPlan), and
            _should_ be serialized if the planning graph is being used to estimate
            a heuristic
        """
        self._serialize = serialize
        self._is_leveled = False
        self._ignore_mutexes = ignore_mutexes
        self.goal = set(problem.goal)

        # make no-op actions that persist every literal to the next layer
        no_ops = [make_node(n, no_op=True) for n in chain(*(makeNoOp(s) for s in problem.state_map))]
        self._actionNodes = no_ops + [make_node(a) for a in problem.actions_list]
        
        # initialize the planning graph by finding the literals that are in the
        # first layer and finding the actions they they should be connected to
        literals = [s if f else ~s for f, s in zip(state, problem.state_map)]
        layer = LiteralLayer(literals, ActionLayer(), self._ignore_mutexes)
        layer.update_mutexes()
        self.literal_layers = [layer]
        self.action_layers = []
        
    def LevelCost(self, literal_layers, goal):    
        """
        function LevelCost(graph, goal) returns a value
         inputs:
          graph, a leveled planning graph
          goal, a literal that is a goal in the planning graph
        
         for each layeri in graph.literalLayers do
          if goal in layeri then return i
        """
        
        levelCost = 0
        i = 0
             
        for layer in literal_layers:
            GoalFound = False
            if goal in layer:
                GoalFound = True
                levelCost = i
            else:
                i += 1
            if GoalFound:
                break

        return levelCost     

    def h_levelsum(self):
        """ Calculate the level sum heuristic for the planning graph

        The level sum heuristic, following the subgoal independence assumption,
        returns the sum of the level costs of the goals; this is inadmissible
        (not to be allowed or tolerated)
        but works very well in practice for problems that are largely decomposable.
        It is much more accurate than the number-of-unsatisfied-goals heuristic
        from Section 11.2. For our problem, the heuristic estimate for the conjunctive
        goal Have(Cake)∧Eaten(Cake) will be 0+1 = 1, whereas the correct answer is 2.
        Moreover, if we eliminated the Bake(Cake) action, the esimate would
        still be 1, but the conjunctive goal would be impossible
        
        The level sum is the sum of the level costs of all the goal literals
        combined. The "level cost" to achieve any single goal literal is the
        level at which the literal first appears in the planning graph. Note
        that the level cost is **NOT** the minimum number of actions to
        achieve a single goal literal.
        
        For example, if Goal1 first appears in level 0 of the graph (i.e.,
        it is satisfied at the root of the planning graph) and Goal2 first
        appears in level 3, then the levelsum is 0 + 3 = 3.

        Hint: expand the graph one level at a time and accumulate the level
        cost of each goal.

        See Also
        --------
        Russell-Norvig 10.3.1 (3rd Edition)
        """
        
        """
        function LevelSum(graph) returns a value
        
        inputs:
        graph, an initialized (unleveled) planning graph
        
        costs = []
        graph.fill() /* fill the planning graph until it levels off */
        
        for each goal in graph.goalLiterals do
         costs.append(LevelCost(graph, goal))
         
        return sum(costs)
        """
        # TODO: implement this function
        #raise NotImplementedError
        levelCost = 0
        self.fill()
        
        for goal in self.goal:
            #self._extend()
            levelCost += self.LevelCost(self.literal_layers, goal)
            
            #GoalFound = False
            #i = 0
            #for layer in self.literal_layers:
            #    if goal in layer:
            #        GoalFound = True
            #        levelCost += i                    
            #    else:
            #        i += 1
            #if GoalFound:
            #    break

        return levelCost

    def h_maxlevel(self):
        """ Calculate the max level heuristic for the planning graph

        To estimate the cost of a conjunction of goals, there are three simple approaches.
        The MAX-LEVEL max-level heuristic simply takes the maximum level cost of any of
        the goals; this is admissible, but not necessarily very accurate.
        
        The max level is the largest level cost of any single goal fluent.
        The "level cost" to achieve any single goal literal is the level at
        which the literal first appears in the planning graph. Note that
        the level cost is **NOT** the minimum number of actions to achieve
        a single goal literal.

        For example, if Goal1 first appears in level 1 of the graph and
        Goal2 first appears in level 3, then the levelsum is max(1, 3) = 3.

        Hint: expand the graph one level at a time until all goals are met.

        See Also
        --------
        Russell-Norvig 10.3.1 (3rd Edition)

        Notes
        -----
        WARNING: you should expect long runtimes using this heuristic with A*
        """
        
        """
        function MaxLevel(graph) returns a value
         inputs:
          graph, an initialized (unleveled) planning graph
        
         costs = []
         graph.fill() /* fill the planning graph until it levels off */
         for each goal in graph.goalLiterals do
          costs.append(LevelCost(graph, goal))
         return max(costs)
        """
        
        # TODO: implement maxlevel heuristic
        #raise NotImplementedError
        levelCost = 0
        maxLevelCost = levelCost
        self.fill()
        
        for goal in self.goal:
            #self._extend()
            levelCost = self.LevelCost(self.literal_layers, goal)
            
            #GoalFound = False
            #i = 0
            #for layer in self.literal_layers:
            #    if goal in layer:
            #        GoalFound = True
            #        levelCost += i                    
            #    else:
            #        i += 1
            #if GoalFound:
            if maxLevelCost < levelCost:
                maxLevelCost = levelCost                
                
        return maxLevelCost
    
    def h_setlevel(self):
        """ Calculate the set level heuristic for the planning graph
        
        the set-level heuristic finds the level at which all the
        literals in the conjunctive goal appear in the planning graph without any pair
        of them being mutually exclusive. This heuristic gives the correct values of 2 for
        our original problem and infinity for the problem without Bake(Cake). It dominates
        the max-level heuristic and works extremely well on tasks in which there is a good
        deal of interaction among subplans

        The set-level heuristic finds the level at which all the literals in the conjunctive goal
        appear in the planning graph without any pair of them being mutually exclusive.

        The set level of a planning graph is the first level where all goals
        appear such that no pair of goal literals are mutex in the last
        layer of the planning graph.

        Hint: expand the graph one level at a time until you find the set level

        See Also
        --------
        Russell-Norvig 10.3.1 (3rd Edition)

        Notes
        -----
        WARNING: you should expect long runtimes using this heuristic on complex problems
        """
        """
        function SetLevel(graph) returns a value
         inputs:
          graph, an initialized (unleveled) planning graph
        
         graph.fill() /* fill the planning graph until it levels off */
         for layeri in graph.literalLayers do
          allGoalsMet <- true
          for each goal in graph.goalLiterals do
           if goal not in layeri then allGoalsMet <- false
          if not allGoalsMet then continue
        
          goalsAreMutex <- false
          for each goalA in graph.goalLiterals do
           for each goalB in graph.goalLiterals do
            if layeri.isMutex(goalA, goalB) then goalsAreMutex <- true
          if not goalsAreMutex then return i
        
        
        """

        #"""
        self.fill()
        i = -1
        for layer in self.literal_layers:
            i += 1
            allGoalsMet = True
            for goal in self.goal:
                if goal not in layer:
                    allGoalsMet = False
            if not allGoalsMet:
                continue
            goalsAreMutex = False
            #for goalA in self.goal:
            for goalA, goalB in combinations(self.goal, 2):
                #for goalB in self.goal:
                if layer.is_mutex(goalA, goalB):# and goalA != goalB:
                    goalsAreMutex = True
            if not goalsAreMutex:
                return i  
                
        #""" 

    ##############################################################################
    #                     DO NOT MODIFY CODE BELOW THIS LINE                     #
    ##############################################################################

    def fill(self, maxlevels=-1):
        """ Extend the planning graph until it is leveled, or until a specified number of
        levels have been added

        Parameters
        ----------
        maxlevels : int
            The maximum number of levels to extend before breaking the loop. (Starting with
            a negative value will never interrupt the loop.)

        Notes
        -----
        YOU SHOULD NOT THIS FUNCTION TO COMPLETE THE PROJECT, BUT IT MAY BE USEFUL FOR TESTING
        """
        while not self._is_leveled:
            if maxlevels == 0: break
            self._extend()
            maxlevels -= 1
        return self

    def _extend(self):
        """ Extend the planning graph by adding both a new action layer and a new literal layer

        The new action layer contains all actions that could be taken given the positive AND
        negative literals in the leaf nodes of the parent literal level.

        The new literal layer contains all literals that could result from taking each possible
        action in the NEW action layer.
        """
        if self._is_leveled: return

        parent_literals = self.literal_layers[-1]
        parent_actions = parent_literals.parent_layer
        action_layer = ActionLayer(parent_actions, parent_literals, self._serialize, self._ignore_mutexes)
        literal_layer = LiteralLayer(parent_literals, action_layer, self._ignore_mutexes)

        for action in self._actionNodes:
            # actions in the parent layer are skipped because are added monotonically to planning graphs,
            # which is performed automatically in the ActionLayer and LiteralLayer constructors
            if action not in parent_actions and action.preconditions <= parent_literals:
                action_layer.add(action)
                literal_layer |= action.effects

                # add two-way edges in the graph connecting the parent layer with the new action
                parent_literals.add_outbound_edges(action, action.preconditions)
                action_layer.add_inbound_edges(action, action.preconditions)

                # # add two-way edges in the graph connecting the new literaly layer with the new action
                action_layer.add_outbound_edges(action, action.effects)
                literal_layer.add_inbound_edges(action, action.effects)

        action_layer.update_mutexes()
        literal_layer.update_mutexes()
        self.action_layers.append(action_layer)
        self.literal_layers.append(literal_layer)
        self._is_leveled = literal_layer == action_layer.parent_layer

