import bpy
import glob
import numpy as np 
import random 


###########################################################################
# Helpers 

def delete_create_collection(generation_name):
    """
    Deletes or creates a collection. If collection exists then it will delete all children objects in that collection 
    """

    
    #delete the collection if it exists
    collection_idx = bpy.data.collections.find(generation_name)
    
    if collection_idx > -1:
        selected_collection = bpy.data.collections[collection_idx]
        #delete the collection if it exists
        while len(selected_collection.objects) > 0: 
            bpy.data.objects.remove(selected_collection.objects[0])
        bpy.data.collections.remove(selected_collection)

    #create a collection to hold all these items
    my_coll = bpy.data.collections.new(generation_name)
    bpy.context.scene.collection.children.link(my_coll)
    
    collection_idx = bpy.data.collections.find(generation_name) 
    return (collection_idx, my_coll)

def obj_properties(obj): 
    #get the object color
    (r,g,b,a) = obj.active_material.diffuse_color
    
    #get the dimensions
    (x,y,z) = obj.dimensions
    
    return np.array([r,g,b,a,x,y,z])

def update_object_from_properties(obj, desired_properties):
    """
    Update an object from among a set of properties 
    """
    matg = bpy.data.materials.new(f"Mat {obj.name}")
    matg.diffuse_color = (desired_properties[0], desired_properties[1], desired_properties[2], desired_properties[3])
    
    #set the object color    
    obj.active_material = matg
    
    #set the dimensions
    obj.dimensions = [desired_properties[4], desired_properties[5], desired_properties[6]]
    
###########################################################################
# Genetic Algorithm functions 

def load(generation_name = "parents", model_dir = '/Users/schultz/Desktop/git/learning3D/data/', obj_name_filter="default*.obj"):
    """
    Load the initial set of objects to form the basis of all future generations
    """ 
    
    #delete the collection if it exists
    (collection_idx, my_coll) = delete_create_collection(generation_name)

    # Specify OBJ files
    model_files = glob.glob(model_dir + obj_name_filter)

    for idx, f in enumerate(model_files):
        #load object from file
        bpy.ops.wm.obj_import(filepath = f)

        #select active object
        curr_obj = bpy.context.object
        
        #rename existing object
        curr_obj.name = f"Obj {idx}"
        
        #reposition the object
        curr_obj.location = [0, 6*idx, 0]

        #add it to a collection
        bpy.ops.object.move_to_collection(collection_index=collection_idx+1)


    
def fitness(obj):
    """
    Score an object based on its fitness (closeness to end goal)
    """
    
    #set the ideal r,g,b,a,x,y,z
    ideal = np.array([0.72, 0.274, 0.801, 1, 2, 2, 2])
    current = obj_properties(obj)
    
    return 1/ (np.linalg.norm(ideal-current) +0.0000000001)
    
def crossover_properties(obj1, obj2):
    """
    Create a set of properties derived from a uniform crossover from two objects

    returns: an np.array of properties [r,g,b,a,x,y,z]
    """
    obj1_props = obj_properties(obj1)
    obj2_props = obj_properties(obj2)
    
    child_props = np.zeros_like(obj1_props)
    #use uniform crossover
    for i in range(len(child_props)):
        if random.random() <= .5:
            child_props[i]=obj1_props[i]
        else:
            child_props[i]=obj2_props[i]
    
    return child_props
    
def mutation_properties(obj):
    """
    Create a set of properties derived from a uniform crossover from two objects

    returns: an np.array of properties [r,g,b,a,x,y,z]
    """
    obj_props = obj_properties(obj)

    for i in range(len(obj_props)):
        if random.random() <= 1/len(obj_props):
            if i < 4:
                #colors are between 0 and 1 
                obj_props[i] = random.random()
            else:
                #dimensions can go up to 10
                obj_props[i] = random.randint(0,10)

    return obj_props


def create_generation(generation_idx, n_population, mutate_probability = 0.1, keep_last = 5):
    
    generation_name = f"generation {generation_idx}"
    (collection_idx, my_coll) = delete_create_collection(generation_name)
    
    #find prior generation (or parents generation if no others exist)
    prior_generation = bpy.data.collections.find(f"generation {generation_idx-1}") 
    if prior_generation == -1:
        prior_generation = bpy.data.collections.find(f"parents")
     
    
    #score all objects in the prior generation (as probabilities) 
    obj_scores = np.array([fitness(obj) for obj in bpy.data.collections[prior_generation].objects])
    obj_scores = obj_scores / np.sum(obj_scores)
    
    
    #generate n_population items in this generation (assigning them to the correct layer)
    while len(bpy.data.collections[collection_idx].objects) < n_population:
        #find two according to fitness
        obj_to_cross = np.random.choice(len(obj_scores), 2, replace=False, p=obj_scores)

        #create an off spring
        offspring_data = bpy.data.collections[prior_generation].objects[obj_to_cross[0]].data.copy()
        offspring = bpy.data.collections[prior_generation].objects[obj_to_cross[0]].copy()
        offspring.data = offspring_data

        #reposition the object
        offspring.location = [generation_idx*10, 6*len(bpy.data.collections[collection_idx].objects), 0]

        #make a new 
        offspring_properties = crossover_properties(bpy.data.collections[prior_generation].objects[obj_to_cross[0]],
                                              bpy.data.collections[prior_generation].objects[obj_to_cross[1]])
        update_object_from_properties(offspring, offspring_properties)

        #mutate if needed
        #if random.random() <  mutate_probability:
        #    offspring_properties = mutation_properties(offspring)
        #    update_object_from_properties(offspring, offspring_properties)
        offspring["fitness"] = fitness(offspring)

        #add to next gen
        bpy.data.collections[collection_idx].objects.link(offspring)


load()

for i in range(10):
    create_generation(i, 20)

