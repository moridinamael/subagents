# -*- coding: utf-8 -*-
"""
Created on Fri May 10 14:09:30 2019

@author: Matt
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Apr 04 09:26:27 2019

@author: mfreeman
"""

import random
import math
import matplotlib.pyplot as plt
import copy

class position():
    def __init__(self,x,y):
        self._x = x
        self._y = y

def distance(a,b):
    return math.sqrt((a._x-b._x)*(a._x-b._x) + (a._y-b._y)*(a._y-b._y))

class agent():
    def __init__(self,location,goals=[],beliefs=[],ply2=False,color="default"):
        self._goals = goals
        self._beliefs = beliefs
        self._location = location
        self._prev_locations = [location,location,location,location,location]
        self._average_velocity = 0.0
        self._suffering = 0.0
        for a_goal in self._goals:
            if a_goal._pinned == True:
                a_goal._preferred_location = self._prev_locations[-2]
        self._loc_hist_x = []
        self._loc_hist_y = []
        self._loc_hist_c = []
        self._ply2 = ply2
        self._color = color

    def random_movement_options(self,count=10):
        self._current_options = []
        self._current_options_new_pos = []
        for ii in range(0,count):
            x = random.uniform(-1.0,1.0)
            y = math.sqrt(1.0-x*x) * random.choice([-1.0,1.0])

            option = position(x,y)
            self._current_options.append(option)
            self._current_options_new_pos.append(position(option._x+self._location._x,option._y+self._location._y))

    def ply2_movement_options(self,count=10):
        self._ply2options = {}
        for pos in self._current_options_new_pos:
            self._ply2options[pos] = []
            for jj in range(0,count):
                x = random.uniform(-1.0,1.0)
                y = math.sqrt(1.0-x*x) * random.choice([-1.0,1.0])
                ply2option = position(x+pos._x,y+pos._y)
                #ply2option = position(pos._x+pos._x-self._location._x,pos._y+pos._y-self._location._y)

                self._ply2options[pos].append(ply2option)

    def update_average_velocity(self):
        self._average_velocity = distance(self._location,self._prev_locations[0])/5.0

    def update_position(self,new_pos):
        self._prev_locations.pop(0)
        self._prev_locations.append(self._location)
        self._location = new_pos

    def best_option_by_goal_winner_take_all(self):

        overall_strongest_valence = 0.0
        #print "New Timestep"
        for a_goal in self._goals:
            #print "    New goal"
            current_strongest_valence = -9999999999999999.0
            current_strongest_ply2_valence = -9999999999999999.0
            for option in self._current_options_new_pos:
                velocity_current = distance(option,self._prev_locations[1])/5.0

                if self._ply2 == True:
                    #print "        New Option"
                    for option2ply in self._ply2options[option]:
                        #print "            New 2ply"
                        distance_ply2 = distance(a_goal._preferred_location,option2ply)
                        option_ply2_valence = a_goal.compute_total_valence(distance_ply2,velocity_current)
                        #print "                ",distance_ply2, option_ply2_valence, current_strongest_ply2_valence,current_strongest_valence,overall_strongest_valence
                        if(option_ply2_valence > current_strongest_ply2_valence):
                            current_strongest_ply2_valence = option_ply2_valence
                    if(current_strongest_ply2_valence > current_strongest_valence):
                        current_strongest_valence = current_strongest_ply2_valence
                        #print "New top current_strongest_valence",current_strongest_valence
                        best_option = option
                else:
                    distance_current = distance(a_goal._preferred_location,option)
                    option_valence = a_goal.compute_total_valence(distance_current,velocity_current)

                    if(option_valence > current_strongest_valence):
                        current_strongest_valence = option_valence
                        best_option = option


            if(abs(current_strongest_valence) > overall_strongest_valence):
                overall_strongest_valence = abs(current_strongest_valence)
                best_new_pos = best_option

        return best_new_pos,overall_strongest_valence

    def best_option_by_goal_summation(self):
        current_strongest_valence = -9999999999999999.0
        for option in self._current_options_new_pos:
            option_summed_valence = 0.0
            for a_goal in self._goals:
                distance_current = distance(a_goal._preferred_location,option)
                velocity_current = distance(option,self._prev_locations[1])/5.0
                option_valence = a_goal.compute_total_valence(distance_current,velocity_current) #compute_distance_valence(distance_current)
                option_summed_valence += option_valence
                if(option_summed_valence > current_strongest_valence):
                    current_strongest_valence = option_summed_valence
                    best_option = option

        return best_option,current_strongest_valence


    def compute_suffering(self):
        self._suffering = 0.0
        for a_goal in self._goals:
            current_distance = distance(a_goal._preferred_location,self._location)
            current_velocity = distance(self._location,self._prev_locations[0])/5.0
            self._suffering += a_goal.compute_total_valence(current_distance,current_velocity)
        return self._suffering

    def update_agent_satisfaction(self):
        for a_goal in self._goals:
            a_goal.update_satisfaction()
            distance_current = distance(a_goal._preferred_location,self._location)
            velocity_current = distance(self._prev_locations[0],self._location)/5.0
            a_goal.detect_distance_satisfaction_acheivement(distance_current)
            a_goal.detect_velocity_satisfaction_acheivement(velocity_current)

class goal_like():
    def __init__(self,
                 base_dist_metric,
                 dist_decay,
                 base_time_metric,
                 time_decay,
                 preferred_location,
                 satisfaction_threshold,
                 base_velocity_metric=0.0,
                 min_velocity=-1.0,
                 subgoals=[]):
        self._base_dist_metric = base_dist_metric
        self._dist_decay = dist_decay
        self._base_time_metric = base_time_metric
        self._time_decay = time_decay

        self._pinned = False
        self._has_friend = False
        if type(preferred_location) == type("pinned"):
            if preferred_location == "pinned":
                self._pinned = True
            elif preferred_location == "friend":
                self._has_friend = True
            else:
                print "INVALID PREFERRED_LOCATION"
        else:
            self._preferred_location = preferred_location
            self._pinned = False
        self._base_velocity_metric = base_velocity_metric
        self._min_velocity = min_velocity

        self._satisfaction_threshold = satisfaction_threshold
        self._satisfaction = 0.0
        self._subgoals = subgoals

    def detect_distance_satisfaction_acheivement(self,current_distance):
        if current_distance < self._satisfaction_threshold:
            self._satisfaction = 1.0

    def set_friend(self,friend):
        self._friend = friend

    def detect_velocity_satisfaction_acheivement(self,current_velocity):
        if self._min_velocity < 0.0:
            return 0.0
        elif current_velocity > self._min_velocity:
            self._satisfaction = 1.0
            return 0.0
        else:
            return 1.0


    def compute_total_valence(self,current_distance,current_velocity):
        distance_valence = self.compute_distance_valence(current_distance)
        velocity_valence = self.compute_velocity_valence(current_velocity)
        time_valence_mod = self.compute_time_valence_modifier(current_distance)

        return ( distance_valence + velocity_valence ) * time_valence_mod

    def compute_distance_valence(self,current_distance):
        return self._base_dist_metric / pow(current_distance,self._dist_decay)

    def compute_velocity_valence(self,current_velocity):
        return self._base_velocity_metric * self.detect_velocity_satisfaction_acheivement(current_velocity)

    def compute_time_valence_modifier(self,current_distance):
        return self._base_time_metric * ( 1.0 - self._satisfaction )

    def update_satisfaction(self):
        self._satisfaction = self._satisfaction * self._time_decay

#class belief_like():

class world():
    def __init__(self,agents,choice_option="winner_take_all"):
        self._agents = agents
        self._choice_option = choice_option

    def update_world(self,count):
        for an_agent in self._agents:
            an_agent._loc_hist_x.append(an_agent._location._x)
            an_agent._loc_hist_y.append(an_agent._location._y)
            an_agent._loc_hist_c.append(count)

            an_agent.random_movement_options()

            # Must update preferred locations before search for best option.
            for a_goal in an_agent._goals:
                if a_goal._pinned == True:
                    a_goal._preferred_location = an_agent._prev_locations[-2]
                elif a_goal._has_friend == True:
                    a_goal._preferred_location = a_goal._friend._location

            if(an_agent._ply2 == True):
                an_agent.ply2_movement_options()
            if self._choice_option == "winner_take_all":
                best_new_pos, strongest_valence = an_agent.best_option_by_goal_winner_take_all()
            elif self._choice_option == "summation":
                best_new_pos, strongest_valence = an_agent.best_option_by_goal_summation()

            an_agent.update_position(best_new_pos)
            an_agent.update_average_velocity()

            an_agent.update_agent_satisfaction()



    def run_world(self,timesteps):
        for kk in range(0,timesteps):
            self.update_world(kk)

    def plot_world(self):
        plt.figure(figsize=(10,10))
        
        for an_agent in self._agents:

            for a_goal in an_agent._goals:
                x = a_goal._preferred_location._x
                y = a_goal._preferred_location._y
                radius = a_goal._satisfaction_threshold
                if a_goal._base_dist_metric < 0.0:
                    color = "r"
                    size = 50.0*50.0
                else:
                    color = "g"
                    size = radius*radius*radius*radius*2
                plt.scatter(x,y,s=size,c=color)

        for an_agent in self._agents:
            if(an_agent._color == "default"):
                plt.scatter(an_agent._loc_hist_x,an_agent._loc_hist_y,c=an_agent._loc_hist_c,cmap="Accent",s=4.0,linewidths=0.0) #,marker=".",linestyle="")
            else:
                plt.scatter(an_agent._loc_hist_x,an_agent._loc_hist_y,c=an_agent._color,s=4.0,linewidths=0.0) #,marker=".",linestyle="")
               
        plt.ylim([-10,70])
        plt.xlim([-40,40])
        
        plt.axis('off')


lowest_suffering = 99999999999999.0

for jj in range(0,1):

    """
    trial_x,trial_y,trial_a,trial_threshold = random.uniform(0.0,1.0) * 100.0, random.uniform(0.0,1.0) * 100.0,random.uniform(-5.0,5.0),random.uniform(0.0,10.0)
    goal_t = goal_like(trial_a, 2.0, 1.0,0.999,position(trial_x,trial_y),trial_threshold)   # generic
    cumulative_suffering = 0.0
    """

    """
    Changing repulsive valence from -0.4 to -0.5 makes the difference in whether it will ever reach the upper goalstate.
    """
    goal_1 = goal_like(1.000,  2.0, 1.0,0.99,position(-15.0,15.0),5.0)   # attractive
    goal_2 = goal_like(1.745,  2.0, 1.0,0.99,position(15.0,15.0), 5.0)   # attractive
    goal_3 = goal_like(-0.4,   1.5, 0.15,0.8,  position(0.0,27.0),  0.0)  # repulsive
    goal_4 = goal_like(1.745,  2.0, 1.0,0.99,position(0.0,60.0), 5.0)    # attractive
    goal_5 = goal_like(0.000,  2.0, 1.0,0.1,position(0.0,0.0), 0.0, base_velocity_metric=1.0, min_velocity = 0.0)    # velocity


    agent_1 = agent(location=position(0.0,0.0),goals=[goal_1,goal_2,goal_3,goal_4,goal_5],beliefs=[])

    world_0a = world([agent_1])

    # Aversive obstacle
    goal_1 = goal_like(1.000,  2.0, 1.0,0.99,position(-15.0,15.0),5.0)   # attractive
    goal_2 = goal_like(1.745,  2.0, 1.0,0.99,position(15.0,15.0), 5.0)   # attractive
    goal_3 = goal_like(-0.7,   1.5, 0.15,0.8,  position(0.0,27.0),  0.0)  # repulsive
    goal_4 = goal_like(1.745,  2.0, 1.0,0.99,position(0.0,60.0), 5.0)    # attractive
    goal_5 = goal_like(0.000,  2.0, 1.0,0.1,position(0.0,0.0), 0.0, base_velocity_metric=1.0, min_velocity = 0.0)    # velocity


    agent_1 = agent(location=position(0.0,0.0),goals=[goal_1,goal_2,goal_3,goal_4,goal_5],beliefs=[])

    world_0b = world([agent_1])

    # Avoid obstacle
    goal_1 = goal_like(1.000,  2.0, 1.0,0.99,position(-15.0,15.0),5.0)   # attractive
    goal_2 = goal_like(1.745,  2.0, 1.0,0.99,position(15.0,15.0), 5.0)   # attractive
    goal_3 = goal_like(-0.7,   1.5, 0.15,0.8,  position(0.0,27.0),  0.0)  # repulsive
    goal_4 = goal_like(1.745,  2.0, 1.0,0.99,position(0.0,60.0), 5.0)    # attractive
    goal_4b = goal_like(1.0,  2.0, 1.0,0.99,position(20.0,40.0), 5.0)    # attractive
    goal_5 = goal_like(0.000,  2.0, 1.0,0.1,position(0.0,0.0), 0.0, base_velocity_metric=1.0, min_velocity = 0.0)    # velocity


    agent_1 = agent(location=position(0.0,0.0),goals=[goal_1,goal_2,goal_3,goal_4,goal_4b],beliefs=[])

    world_0c = world([agent_1])


    # With a cell phone

    goal_1 = goal_like(1.000,  2.0, 1.0,0.999,position(-15.0,15.0),5.0)   # attractive
    goal_2 = goal_like(1.745,  2.0, 1.0,0.999,position(15.0,15.0), 5.0)   # attractive
    goal_3 = goal_like(-0.4,   1.5, 0.15,0.8,  position(0.0,27.0),  0.0)  # repulsive
    goal_4 = goal_like(1.745,  2.0, 1.0,0.99,position(0.0,60.0), 5.0)    # attractive
    goal_5 = goal_like(0.000,  2.0, 1.0,0.1,position(0.0,0.0), 0.0, base_velocity_metric=1.0, min_velocity = 0.0)    # velocity
    goal_cell = goal_like(0.0010,  2.0, 1.0,0.9,"pinned", 0.0)    # cell phone



    agent_1 = agent(location=position(0.0,0.0),goals=[goal_1,goal_2,goal_3,goal_4,goal_5,goal_cell],beliefs=[])

    world_1 = world([agent_1])

    # With a high movement preference

    goal_1 = goal_like(1.000,  2.0, 1.0,0.999,position(-15.0,15.0),5.0)   # attractive
    goal_2 = goal_like(1.745,  2.0, 1.0,0.999,position(15.0,15.0), 5.0)   # attractive
    goal_3 = goal_like(-0.4,   1.5, 0.15,0.8,  position(0.0,27.0),  0.0)  # repulsive
    goal_4 = goal_like(1.745,  2.0, 1.0,0.99,position(0.0,60.0), 5.0)    # attractive
    goal_5 = goal_like(0.000,  2.0, 1.0,0.1,position(0.0,0.0), 0.0, base_velocity_metric=1.0, min_velocity = 0.8)    # velocity
    #goal_cell = goal_like(0.10,  2.0, 1.0,0.5,"pinned", 0.0)    # cell phone

    agent_1 = agent(location=position(0.0,0.0),goals=[goal_1,goal_2,goal_3,goal_4,goal_5],beliefs=[])

    world_2a = world([agent_1])

    # With a moderate movement preference

    goal_1 = goal_like(1.000,  2.0, 1.0,0.999,position(-15.0,15.0),5.0)   # attractive
    goal_2 = goal_like(1.745,  2.0, 1.0,0.999,position(15.0,15.0), 5.0)   # attractive
    goal_3 = goal_like(-0.4,   1.5, 0.15,0.8,  position(0.0,27.0),  0.0)  # repulsive
    goal_4 = goal_like(1.745,  2.0, 1.0,0.99,position(0.0,60.0), 5.0)    # attractive
    goal_5 = goal_like(0.000,  2.0, 1.0,0.1,position(0.0,0.0), 0.0, base_velocity_metric=1.0, min_velocity = 0.3)    # velocity
    #goal_cell = goal_like(0.10,  2.0, 1.0,0.5,"pinned", 0.0)    # cell phone

    agent_1 = agent(location=position(0.0,0.0),goals=[goal_1,goal_2,goal_3,goal_4,goal_5],beliefs=[])

    world_2b = world([agent_1])


    """
    Changing repulsive valence from -0.4 to -0.5 makes the difference in whether it will ever reach the upper goalstate.
    """
    goal_1 = goal_like(1.000,  2.0, 1.0,0.999,position(-15.0,15.0),5.0)   # attractive
    goal_2 = goal_like(1.000,  2.0, 1.0,0.999,position(15.0,15.0), 5.0)   # attractive
    #goal_3 = goal_like(-0.4,   1.5, 0.15,0.8,  position(0.0,27.0),  0.0)  # repulsive
    goal_4 = goal_like(1.000,  2.0, 1.0,0.999,position(0.0,60.0), 5.0)    # attractive
    #goal_5 = goal_like(0.000,  2.0, 1.0,0.1,position(0.0,0.0), 0.0, base_velocity_metric=1.0, min_velocity = 0.0)    # velocity
    goal_6 = goal_like(1.000,  2.0, 1.0,0.999,position(50.0,70.0), 5.0)    # attractive


    agent_1 = agent(location=position(0.0,0.0),goals=[goal_1,goal_2,goal_4,goal_6],beliefs=[],ply2=False,color='b')
    agent_2 = agent(location=position(0.0,0.0),goals=[goal_1,goal_2,goal_4,goal_6],beliefs=[],ply2=True,color='r')
    #agent_3 = agent(location=position(0.0,0.0),goals=[goal_1,goal_2,goal_4],beliefs=[],ply2=False,color='g')

    world_3 = world([copy.deepcopy(agent_1),copy.deepcopy(agent_2)])

    # With higher satisfiability

    goal_1 = goal_like(1.000,  2.0, 1.0,0.99,position(-15.0,15.0),5.0)   # attractive
    goal_2 = goal_like(1.745,  2.0, 1.0,0.99,position(15.0,15.0), 5.0)   # attractive
    goal_3 = goal_like(-35.0,   3.0, 0.15,0.8,  position(0.0,27.0),  0.0)  # repulsive
    goal_4 = goal_like(1.745,  2.0, 1.0,0.99,position(0.0,60.0), 5.0)    # attractive
    #goal_5 = goal_like(0.000,  2.0, 1.0,0.1,position(0.0,0.0), 0.0, base_velocity_metric=1.0, min_velocity = 0.3)    # velocity
    #goal_cell = goal_like(0.10,  2.0, 1.0,0.5,"pinned", 0.0)    # cell phone

    agent_1 = agent(location=position(0.0,0.0),goals=[goal_1,goal_2,goal_3,goal_4],beliefs=[])

    world_4 = world([agent_1])


    # Lovers

    goal_1        = goal_like(1.000,  2.0, 1.0,0.999,position(-15.0,15.0),5.0)   # attractive
    goal_2a       = goal_like(1.745,  2.0, 1.0,0.999,position(15.0,15.0), 5.0)   # attractive
    goal_2b       = goal_like(1.745,  2.0, 1.0,0.999,position(15.0,15.0), 5.0)   # attractive
    goal_3a       = goal_like(-0.4,   1.5, 0.15,0.8,  position(0.0,27.0),  0.0)  # repulsive
    goal_3b       = goal_like(-0.4,   1.5, 0.15,0.8,  position(0.0,27.0),  0.0)  # repulsive
    goal_4        = goal_like(1.745,  2.0, 1.0,0.99,position(0.0,60.0), 5.0)    # attractive
    goal_friend_a = goal_like(0.1,    2.0, 1.0,0.99,"friend", 0.0)    # a friend
    goal_friend_b = goal_like(0.1,    2.0, 1.0,0.99,"friend", 0.0)    # a friend



    agent_a = agent(location=position(0.0,0.0),goals=[goal_1,goal_2a,goal_3a,goal_friend_a],beliefs=[],color='r')
    agent_b = agent(location=position(0.0,0.0),goals=[goal_2b,goal_3b,goal_4,goal_friend_b],beliefs=[],color='b')

    agent_a._goals[3].set_friend(agent_b)
    agent_b._goals[3].set_friend(agent_a)

    world_5 = world([agent_a,agent_b])

    # Friends

    goal_1        = goal_like(1.000,  2.0, 1.0,0.999,position(-15.0,15.0),5.0)   # attractive
    goal_2a       = goal_like(1.745,  2.0, 1.0,0.999,position(15.0,15.0), 5.0)   # attractive
    goal_2b       = goal_like(1.745,  2.0, 1.0,0.999,position(15.0,15.0), 5.0)   # attractive
    #goal_3a       = goal_like(-0.2,   1.5, 0.15,0.8,  position(0.0,27.0),  0.0)  # repulsive
    #goal_3b       = goal_like(-0.2,   1.5, 0.15,0.8,  position(0.0,27.0),  0.0)  # repulsive
    goal_4        = goal_like(1.745,  2.0, 1.0,0.999,position(0.0,60.0), 5.0)    # attractive
    goal_friend_a = goal_like(0.1,    2.0, 1.0,0.99,"friend", 0.5)    # a friend
    goal_friend_b = goal_like(0.1,    2.0, 1.0,0.99,"friend", 0.5)    # a friend

    """
    goal_optima = goal_like(-2.7857, 2.0, 1.0,0.999,position(35.248,26.075),1.4493)   # generic
    """

    agent_a = agent(location=position(0.0,0.0),goals=[goal_1,goal_2a,goal_friend_a],beliefs=[],color='r')
    agent_b = agent(location=position(0.0,0.0),goals=[goal_2b,goal_4,goal_friend_b],beliefs=[],color='b')

    agent_a._goals[2].set_friend(agent_b)
    agent_b._goals[2].set_friend(agent_a)

    world_6 = world([agent_a,agent_b])

    # New goals are disruptive (contrast with #1)

    goal_1 = goal_like(1.000,  2.0, 1.0,0.99,position(-15.0,15.0),5.0)   # attractive
    goal_2 = goal_like(1.745,  2.0, 1.0,0.99,position(15.0,15.0), 5.0)   # attractive
    goal_3 = goal_like(-0.4,   1.5, 0.15,0.8,  position(0.0,27.0),  0.0)  # repulsive
    goal_4 = goal_like(1.745,  2.0, 1.0,0.99,position(0.0,60.0), 5.0)    # attractive
    goal_4b = goal_like(2.745,  2.0, 1.0,0.99,position(30.0,60.0), 5.0)    # attractive  # New "disruptive" goal
    goal_5 = goal_like(0.000,  2.0, 1.0,0.1,position(0.0,0.0), 0.0, base_velocity_metric=1.0, min_velocity = 0.0)    # velocity


    agent_1 = agent(location=position(0.0,0.0),goals=[goal_1,goal_2,goal_3,goal_4,goal_4b,goal_5],beliefs=[])

    world_7 = world([agent_1])

    # Summation choice option

    world_8 = world([copy.deepcopy(agent_1)],choice_option="summation")

    # Beliefs ... concept of meta-motivational expectation decay as you hedonically adapt
    # to the pursuit of the goal as being status quo/baseline.

    iterations = 10000


    print "Baseline"
    world_0a.run_world(iterations)
    world_0a.plot_world()
    plt.show()

    print "Aversive obstacle"
    world_0b.run_world(iterations)
    world_0b.plot_world()
    plt.show()

    print "Avoid obstacle"
    world_0c.run_world(iterations)
    world_0c.plot_world()
    plt.show()

    
    print "Cell phone"
    world_1.run_world(iterations)
    world_1.plot_world()
    plt.show()

    print "High movement preference"
    world_2a.run_world(iterations)
    world_2a.plot_world()
    plt.show()

    print "Moderate movement preference"
    world_2b.run_world(iterations)
    world_2b.plot_world()
    plt.show()

    plt.xlim(-20,60)
    plt.ylim(0,80)

    print "2-ply lookahead in decision making"
    world_3.run_world(iterations)
    world_3.plot_world()
    plt.show()

    print "With higher goal satisfiability"
    world_4.run_world(iterations)
    world_4.plot_world()
    plt.show()


    print "Lovers"
    world_5.run_world(iterations)
    world_5.plot_world()
    plt.show()


    print "Friends"
    world_6.run_world(iterations)
    world_6.plot_world()
    plt.show()
    
    
    print "New goals are disruptive"
    world_7.run_world(iterations)
    world_7.plot_world()
    plt.show()

    print "Summation choice option"
    world_8.run_world(iterations)
    world_8.plot_world()
    plt.show()

    """
    cumulative_suffering += agent_1.compute_suffering()
    """

    """
    print trial_x,trial_y,trial_a,trial_threshold,":",cumulative_suffering
    if cumulative_suffering < lowest_suffering:
        lowest_suffering = cumulative_suffering
        best_case = [trial_x,trial_y,trial_a,trial_threshold,cumulative_suffering]
    """
