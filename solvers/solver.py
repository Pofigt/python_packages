import numpy as np
from python_packages.tools.load_constants_from_file import *

class Solver():
    
    def __init__(self, **kwargs):
        
        if kwargs.get("name") != None:
            self.name = kwargs.get("name")
        else:
            self.name = "DummySolver"
            
        if kwargs.get("t_step") != None:
            self.t_step = kwargs.get("t_step")
        else:
            self.t_step = 0.1
        
        if kwargs.get("t_end") != None:
            self.t_end = kwargs.get("t_end")
        else:
            self.t_end = 100.0
            
        if kwargs.get("frames") != None:
            self.frames = kwargs.get("frames")
        else:
            self.frames = 100
            
        if kwargs.get("ADAPTIVE") != None:
            self.ADAPTIVE = kwargs.get("ADAPTIVE")
        else:
            self.ADAPTIVE = False
             
        self.parameters = [0.01, 0.9, 0.3, 2.0]
        if kwargs.get("parameters") != None:
            self.parameters[0] = kwargs.get("parameters")[0] # tolerance
            self.parameters[1] = kwargs.get("parameters")[1] # margin
            self.parameters[2] = kwargs.get("parameters")[2] # decrement
            self.parameters[3] = kwargs.get("parameters")[3] # increment
        
        if kwargs.get("function") != None:
            self.function = kwargs.get("function")
        else:
            self.function = None                                   
    
    def adapt(self, t_step, delta, params): # adapts time step 
        tol = params[0] # tolerance
        marg = params[1] # magrin from tolerance
        decr = params[2] # maximal decrement
        incr = params[3] # maximum increment
        delta = delta + 0.0000000001 #to avoid division by 0
        return float (t_step * marg * min( max(tol/delta, decr) , incr )  ) # FIX sometimes returns np.float64     

    
    def evolve(self, X, t_step = None):
        pass

    
    
    def simulate(self, X, **kwargs):

        if kwargs.get("ADAPTIVE") == None:
            ADAPTIVE = self.ADAPTIVE
        else:
            ADAPTIVE = kwargs.get("ADAPTIVE")           
            
        if kwargs.get("t_step") != None:
            t_step = kwargs.get("t_step")
            del kwargs["t_step"] # must be deleted for avoiding conflict of arguments in self.evolve() & self.adapt()
        else:
            t_step = self.t_step
        
        
        
        if kwargs.get("t_end") != None:
            t_end = kwargs.get("t_end")
        else:
            t_end = self.t_end
            
        if kwargs.get("frames") != None:
            frames = kwargs.get("frames")
        else:
            frames = self.frames
            

                
        parameters = self.parameters
        if kwargs.get("parameters") != None:
            parameters[0] = kwargs.get("parameters")[0] # tolerance
            parameters[1] = kwargs.get("parameters")[1] # margin
            parameters[2] = kwargs.get("parameters")[2] # decrement
            parameters[3] = kwargs.get("parameters")[3] # increment
                    
        if kwargs.get("SILENT") != None:
            SILENT = kwargs.get("SILENT")
        else:
            SILENT = False
                    
        if kwargs.get("function") != None:
            self.function = kwargs.get("function") # be careful, will rewrite self.function!!
            
        if self.function == None:
            print("function is not given! "+"\n"+"use Method.function = some_function "+"\n"+"EXIT")
            return None, None # out, t_list

        
        if kwargs.get("constants") == None:       
            
            if str(self.function).split()[1] == "fun_points_in_basket":
                print("constants are not specified"+"\n"+"load from 'constants_for_fun_points_in_basket.txt'")
                constants = load_constants_from_file("constants_for_fun_points_in_basket.txt")
                kwargs["constants"] = constants # REWRITING
                
            elif str(self.function).split()[1] == "fun_with_obstacles":
                print("constants are not specified"+"\n"+"load from 'constants_for_fun_with_obstacles.txt'")   
                constants = load_constants_from_file("constants_for_fun_with_obstacles.txt")
                kwargs["constants"] = constants # REWRITING
                
        if kwargs.get("constants") != None:
            constants = kwargs.get("constants")
            for key in sorted(list(constants.keys())):
                print('{0:10}{1}'.format(key, constants[key]))

            
        if kwargs.get("walls") != None:
            walls = kwargs.get("walls")            
            print(walls.vertices_number-1, "walls initialized")
            
        t = 0.0
        t_print = 0.0
        t_list = []
        output = [X]
        
        while (t<=t_end):
            
            if ADAPTIVE == True:
                
                X1 = self.evolve(X,
                                 t_step, **kwargs)
                
                X2 = self.evolve(self.evolve(X, 0.5*t_step, **kwargs),
                                 0.5*t_step, **kwargs)

                delta = np.linalg.norm(X1 - X2) # [:] for instance of Variable class TODO!!!! FOR ANY VECTORS

                t_step = self.adapt(t_step, delta, parameters)
            
            X = self.evolve(X, t_step, **kwargs)
            
            if (t_print >= (t_end / float(frames)) ):
              
                self.make_snapshot(X, output)
                t_print = 0.0
                
                if kwargs.get("output") != None:
                    kwargs.get("output").append(X)
                
                if (SILENT==False):
                    print("{0:.5f} / {1}".format(t,t_end))
                   
            t_print = t_print + t_step      
            t = t + t_step #round(t + t_step , 7) # TODO, avoiding error! Could be a problem if t = 0.00000000xxxx -> 0.0
            #t_list.append(t_step)           
            
        return output, t_list

    
    def make_snapshot(self, X, output):
        output.append( X )       
 

    def __str__(self):
        
        s = ""           
        s = s + self.name + "\n"
        s = s + "t_step = " + str(self.t_step) + "\n"
        s = s + "t_end = " + str(self.t_end) + "\n"
        s = s + "frames = " + str(self.frames) + "\n"
        
        if self.function != None:   
            s = s + "function = " + str(self.function).split()[1]
        else:
            s = s + "function is not given"
        
        if self.ADAPTIVE == True:
            s = "Adaptive" + s + "\n"
            s = s + "parameters = [tol, marg, decr, incr] = " + str(self.parameters)      
        
        return s