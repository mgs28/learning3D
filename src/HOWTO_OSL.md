## Simple functions

You can call functions from a shader as long as the definition happens before the shader function.

    float function(float first, float second)
    {
        return first + second;     
    }


    float second_function(float first, float second)
    {
        return first - second;     
    }

    shader function_call(float a = 0, float b = 0,
                        output float c = 0)
    {
        c=second_function(function(a,b),b);
    }

## Play with objects (e.g. colors)

There are a lot of building in [objects](https://docs.otoy.com/osl/assets/doc/osl-languagespec-1.11.pdf) like color. 

    shader color_add(color a = 0, color b = 0,
        output color c = 0){
        
        c.r = (a.r + b.r)/2;
        c.g = a.g;
        c.b = b.b;  
    }


## Make a circle in the middle

This one gets more fun with using built in [Global Variables (page 44)](https://docs.otoy.com/osl/assets/doc/osl-languagespec-1.11.pdf)  like N and P. 

    shader make_circle(float radius = 0, 
    output color out = 0 ){
        if(distance(P, 0) < radius && distance(P,0) > radius/1.2){
            out = P;
        }else{
            out = 0;
        } 
    }