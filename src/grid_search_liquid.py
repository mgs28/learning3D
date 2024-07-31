
import bpy
import glob
import random 
import math 
from typing import Callable
import os
import logging 
import bisect 

log = logging.getLogger(__name__)

logging.basicConfig(filename=f'{os.path.expanduser("~/Desktop/")}liquid.log', filemode='a', encoding='utf-8', level=logging.INFO)
        
def fitness():
    """
    Need to define a fitness for the object such that a higher score means good things 
    """
    obj = bpy.data.objects["Liquid Domain"]
    target_ratio = math.asin(45/180*math.pi) #looking to make it match a 45* angle splash 
    
    bpy.context.scene.frame_current = 1
    bpy.context.view_layer.update()
    obj["fitness"] = 0
    
    while (bpy.context.scene.frame_current < bpy.context.scene.frame_end):
        bpy.context.view_layer.update()
        if bpy.context.scene.frame_current > 21:

            wl_ratio = obj.dimensions.x / obj.dimensions.y
            curr_fitness = 1 / ((target_ratio - wl_ratio) * (target_ratio - wl_ratio ) + 0.00001) 
            log.debug(f"{bpy.context.scene.frame_current}. fitness = {curr_fitness} for x = {obj.dimensions.x}, y={obj.dimensions.y}")
            obj["fitness"] =  max(obj["fitness"], curr_fitness)
            log.debug(f"fitness at {bpy.context.scene.frame_current} = {curr_fitness}")
        bpy.context.scene.frame_current = bpy.context.scene.frame_current + 1
        
    return obj["fitness"]        

class OptimizationParam:
    """
    An optimization parameter (e.g. a fluid domain) and the properties you wish to iterate over
    """
    obj = None 
    obj_ascii = ""
    properties = {} 
    properties_type = {} 

    def __init__(self, obj:object): 
        self.obj = obj 
        self.obj_ascii = ascii(obj) 
    
    def add_property(self, attribute_name: str, range:list):
        """
        for the object, add an attribute_name and a range of acceptable values. 
           * for numbers, enter a min and max as a list (e.g. [-1,1] to vary from -1 to 1)  
           * for discrete values, enter the relevant values (e.g. ('fluid', 'smoke') to indicate a string value can be "fluid" or "smoke" 
        """
        range.sort()
        self.properties[attribute_name] = range
        self.properties_type[attribute_name] = type(range[0])
    
    def next_val(self, attribute_name: str, curr_val) -> list:
        
        log.debug(f"looking for {curr_val} in {self.properties[attribute_name]}")
        if type(curr_val) == float:
            #error in precision of floats in blender
            curr_val = round(curr_val, 5)
        idx = bisect.bisect_left(self.properties[attribute_name], curr_val)
        log.debug(f"\tfound at {idx}")
        
        return_vals = [] 
        if (idx + 1) < len(self.properties[attribute_name]):
            return_vals.append(self.properties[attribute_name][idx+1])

        if (idx -1) > 0: 
            return_vals.append(self.properties[attribute_name][idx-1])
                               
        return return_vals 
    

def grid_search(obj, fitness: Callable, variables:list[OptimizationParam], max_steps = 10):

    start_fitness = fitness() 

    for i in range(0,max_steps):
        #take a step 
        for var in variables:
            best_step = ""
            best_fitness = fitness() 
            
            for k,val in var.properties.items():
                log.debug(f"{k} = {val}")
                
                original_val = eval(var.obj_ascii + "." + k)
                next_moves = var.next_val(k, original_val)

                for move in next_moves: 
                    move_exec_str = var.obj_ascii + "." + k + f" = {move}"
                    log.debug(f"Thinking about step = {move_exec_str}")
                    exec(move_exec_str)
                    temp_fitness = fitness()
                    if (temp_fitness > best_fitness):
                        best_fitness = max(best_fitness, fitness())
                        best_step = move_exec_str

                #reset the variable to the original value 
                exec(var.obj_ascii + "." + k + f" = {original_val}")

            #take the best step
            if len(best_step) > 0:
                log.info(f"taking step {best_step}")
                log.info(f"\tfitness increased to {best_fitness}")
                exec(best_step)
            else:
                log.info(f"There are no more steps that increase fitness")
                return obj

    return obj 

parameters = OptimizationParam(bpy.context.object.modifiers["Fluid"].domain_settings)

parameters.add_property("use_fractions", [True,False])
parameters.add_property("use_diffusion", [True,False])
parameters.add_property("use_collision_border_back", [True,False])
parameters.add_property("use_collision_border_bottom", [True,False])
parameters.add_property("use_collision_border_front", [True,False])
parameters.add_property("use_collision_border_left", [True,False])
parameters.add_property("use_collision_border_right", [True,False])
parameters.add_property("use_collision_border_top", [True,False])
parameters.add_property("resolution_max", list(range(32,128,16)))  
parameters.add_property("cfl_condition", [x/2 for x in range(1, 10)])  
parameters.add_property("flip_ratio", [x/10 for x in range(1, 20)])  
parameters.add_property("viscosity_base", [x/2 for x in range(1, 20)]) 
parameters.add_property("viscosity_value", [x/2 for x in range(1, 20)]) 
parameters.add_property("surface_tension", [x/10 for x in range(1, 20)]) 

log.info("\n\nStarting...")
log.info(f"Initial Fitness = {fitness()}")
grid_search(bpy.data.objects["Liquid Domain"].modifiers["Fluid"].domain_settings, fitness, [parameters], max_steps = 10)
log.info(f"Final Fitness = {fitness()}")