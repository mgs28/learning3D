import bpy
import glob

def load(generation_name = "parents", model_dir = '/Users/schultz/Desktop/git/learning3D/data/', obj_name_filter="default*.obj"):
    
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

load()