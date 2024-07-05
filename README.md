## Background 

The goal of this project is to learn how to create complex 3D objects where we only know the fitness (e.g. similarity to a physical process) and have some initial Blender objects to evolve from. 

The simple example is to generate a cube shown in the picture below. Each row in the following picture is a generation of the algorithm. The row with three objects in the foreground is the input generation. It is three hand created cubes of different dimensions. The next row is the first generation where there is lots of variability. Each row after that gets a little closer to the end goal (a mauve 2x2x2 cube). Finally, to ease understanding of the rows objects to the right side have a higher fitness than objects to the left end of a row. 

![alt text](documentation\evolve_cube.png "Title")

## Genetic algorithm

In this first iteration (src/cube_evolve.py), we are evolving a cube based on three input objects

* A pure blue cube with x = 0.1, y = 1.5 and z = 1.5 (data/default cube blue)
* A pure green cube with x = 1.5, y = 0.1 and z = 1.5 (data/default cube green)
* A pure red cube with x = 1.5, y = 1.5 and z = 0.1 (data/default cube red)

and are trying to evolve a cube listed in fitness(). The vector ideal is a list of desired attributes starting with color then progressing to dimensions. 

* Color = rgba(0.72, 0.274, 0.801, 1) which is kind of a mauve / pinkish purple
* Size = a cube of 2 units in each direction 

The fitness is scored as a 1/ Euclidean distance by default. There is a very small float to prevent divisions by 0 if we generate the perfect object. You can modify the ideal or fitness score as you wish. The rule of thumb is the final object should be somewhat similar to the input objects. For example, generating a red cube from only green cubes takes longer since it relies on the occassional mutations to introduce a new color. 

    def fitness(obj):
        """
        Score an object based on its fitness (closeness to end goal)
        """
        
        #set the ideal r,g,b,a,x,y,z
        ideal = np.array([0.72, 0.274, 0.801, 1,     2,    2,  2])
        
        current = properties_of_obj(obj)
        
        return 1/ (np.linalg.norm(ideal-current) +0.0000000001)

Each generation is built from the immediately prior generation via two functions: crossover and mutation.

Crossovers take two objects and select attributes from one or the other by tossing a coin. I have chosen to add an averaging crossover step because it helped more rapidly reach desirable outcomes in my tests. 

    def crossover_properties(obj1, obj2):
        """
        Create a set of properties derived from a uniform crossover from two objects

        returns: an np.array of properties [r,g,b,a,x,y,z]
        """
        obj1_props = properties_of_obj(obj1)
        obj2_props = properties_of_obj(obj2)
        
        child_props = np.zeros_like(obj1_props)
        #use uniform crossover
        for i in range(len(child_props)):
            coin = random.random()
            if coin <= .3333333:
                child_props[i]=obj1_props[i]
            elif coin <= .6666666:
                child_props[i]=obj2_props[i]
            else:
                child_props[i]=(obj2_props[i] + obj1_props[i])/2
        
        return child_props

Mutations add some variability into the objects we create to try to reach a global instead of local optimization. You can think of it as an exploration step. 

* If there is no DNA for this attribute (e.g. no red in the color) then it may randomly add some red or it may suddenly add a length or width. 
* If there is already a value in the DNA for an attribuite then it will randomly pick a growth factor that will do anything from 0 out the attribute to triple it.  

It's important to pick a mutation that subtly changes the fitness rather than risks an nonviable solution. 

    def mutation_properties(obj):
        """
        Create a set of properties derived from a uniform crossover from two objects

        returns: an np.array of properties [r,g,b,a,x,y,z]
        """
        obj_props = properties_of_obj(obj)

        for i in range(len(obj_props)):
            if random.random() <= 1/len(obj_props):
                idx = random.randint(0, len(obj_props)-1)
                if obj_props[idx] == 0:
                    if i < 4:
                        #colors are between 0 and 1 
                        obj_props[i] = random.random()
                    else:
                        #dimensions can go up to 10
                        obj_props[i] = random.randint(0,5)
                else:
                    obj_props[i] = obj_props[i] * (random.uniform(0,3))

        return obj_props

The final step is to create a new generation which happens in create_generation(). There is a step which chooses two objects to function as parents. This is done randomly in proportion to fitness so that objects closer to the goal object are more likley to be selected as reproducing pairs. 

    def create_generation(generation_idx, n_population, x_loc, mutate_probability = 0.1):
        
        #[...]
            
        #generate n_population items in this generation (assigning them to the correct layer)
        while len(bpy.data.collections[collection_idx].objects) < n_population:
            #find two according to fitness
            obj_to_cross = np.random.choice(len(obj_scores), 2, replace=False, p=obj_scores)

## Installation

You will also need to install [Blender](https://www.blender.org/download/) and enable [python scripting](https://docs.blender.org/api/current/info_quickstart.html). I am using Python 3. 

You will also need to install a couple of packages into your default python environment to run within Blender.

python -m pip install numpy 


## Running 

Copy the code from src/cube_evolve.py into your Blender scripting environment and hit the play button.

