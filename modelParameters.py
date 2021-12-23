# Number of Iterations
MODEL_NUM_ITERATIONS = 10

# Maximum number of steps before exit
MODEL_MAX_STEPS = 30000

# Final Velocity Tolerance
MODEL_MIN_VELOCITY = 0.2 # lower this number to increase accuracy. The lower the number, the longer the runtime. Must be > 0
MODEL_IN_VELOCITY_THRESHOLD_COUNT = 500

# If the model is not stable (ie, velocities are not in range) discard result
DISCARD_UNSTABLE_RESULTS = True

# BANDOLIER PARAMETERS
"""

        Configuration A         |        Configuration B (note negative x)                 
                                |                  
                / /             |             \ \   
               / /   •  •       |       •  •   \ \  
              / / •  Cell3 •    |    •  Cell3 • \ \ 
             | | •   Pos:   •   |   •   Pos:   • | |
              \ \•(X,Y2+Y1) •   |   •(-X,Y2+Y1)• / /
        •  •   \ \•        •    |    •        • / /  •  •                             
     •  Cell2 • \ \  •  •       |       •  •   / /•  Cell2 •                         
    •   Pos:   • | |            |             | |•   Pos:   •                              
    •   (0,Y2) • / /            |             \ \•   (0,Y2) •        
     •        • / /  •  •       |       •  •   \ \•        •         
        •  •   / /•  Cell1 •    |    •  Cell1 • \ \  •  •            
              | |•   Pos:   •   |   •   Pos:   • | |                            
              \ \•   (X,Y1) •   |   •   (-X,Y1)• / /                         
        •  •   \ \•        •    |    •        • / /   •  •                 
     •  Cell0 • \ \  •  •       |       •  •   / / •  Cell0 •                             
    •   Pos:   • | |            |             | | •   Pos:   •                              
    •   (0,0)  • / /            |             \ \ •   (0,0)  •                         
     •        • / /             |              \ \ •        •        
        •  •   | |              |               | |   •  •                                  
               | |              |               | |            
               | |              |               | |            
               | |              |               | |            

        <<<---------- Direction of stacking <<<----------

"""

# Bandolier cell count
BANDO_CELL_COUNT = 100

# Number of Bandoliers in a module
MODULE_BANDO_COUNT = 9

# Bandolier Designed values (as in CAD)
BANDO_CELL_X = 16 #mm
BANDO_CELL_Y1 = 12 #mm
BANDO_CELL_Y2 = 24 #mm

# Bandolier Tolerance values (measured)
BANDO_X_MU = 0 # mm
BANDO_X_SIGMA = 0.2 # mm
BANDO_Y_MU = 0 # mm
BANDO_Y_SIGMA = 0.3 # mm


# Cell Designed Diameters (as in CAD)
CELL_DIAMETER_18650 = 18 #mm
CELL_DIAMETER_2170 = 21 #mm
CELL_DIAMETER_4680 = 46 #mm
# Cell diameter to be used in the model
CELL_DIAMETER_CURRENT = CELL_DIAMETER_18650

# Cell Tolerance values (measured)
CELL_DIAMETER_MU = 0 # mm
CELL_DIAMETER_SIGMA = 0.001 # mm


# END CONDITION PARAMETERS

"""
                             Configuration A         |        Configuration B (note negative x)                 
                                                     |  

                                  UPPER_X                       UPPER_X
                                     |                             |              
                                _____v                             v  ______     
                                |    |‡|             |             |‡|     |         
                                |    | |             |             | |     |         
                                |    | |             T             | |     |         
         END_CONSTRAINT_UPPER_Y |    | |             O             | |     | END_CONSTRAINT_UPPER_Y        
                                |   / /   •  •       P       •  •   \ \    |         
                                |  / / •  CellN •         •  CellN • \ \   |         
                                | | | •   Pos:   •   E   •   Pos:    • | | |          
                                ‾  \ \•   (X,Yn) •   N   •   (-X,Yn) • / / ‾          
                             •  •   \ \•        •    D    •        • / /  •  •                             
                          •        • \ \  •  •       |       •  •   / /•        •                         
                         •          • | |            |             | |•          •                              
                         •          • / /            |             \ \•          • 
                          •        • / /             |              \ \•        •  
                             •  •   / /              |               \ \  •  •     
                                   / /               |                \ \            
                     *—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*                                                                    
                                              MIDDLE OF BANDOLIER                                   
                     *—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*                                                                 
                                      / /                          \ \       
                                     / /  •  •       |       •  •   \ \      
                                    / /•        •    |    •        • \ \     
                                   | |•          •   B   •          • | |                            
                                   \ \•          •   O   •          • / /                         
                             •  •   \ \•        •    T    •        • / /   •  •                 
                          •  Cell0 • \ \  •  •       T       •  •   / / •  Cell0 •                             
                      _  •   Pos:   • | |            O             | | •   Pos:   • _                             
                      |  •   (0,0)  • / /            M             \ \ •   (0,0)  • |                        
                      |   •        • / /                            \ \ •        •  |      
                      |      •  •   | |              E               | |   •  •     |                             
END_CONSTRAINT_LOWER_Y|             | |              N               | |            |END_CONSTRAINT_LOWER_Y
                      |             | |              D               | |            | 
                      |             |‡|              |               |‡|            | 
                      ‾‾‾‾‾‾‾‾‾‾‾‾‾‾^                                ^  ‾‾‾‾‾‾‾‾‾‾‾‾‾     
                                    |                                |
                           END_CONSTRAINT_LOWER_X           END_CONSTRAINT_LOWER_X
                     
                             <<<---------- Direction of stacking <<<----------

"""


INCLUDE_END_CONSTRAINTS = False

BANDO_DESIRED_SPACING = 30 # from same point to same point

END_CONSTRAINT_LOWER_X = 8
END_CONSTRAINT_UPPER_X = 8
END_CONSTRAINT_LOWER_Y = 30
END_CONSTRAINT_UPPER_Y = 30


"""
                         Configuration A         |        Configuration B (note negative x)                 
                                                 |  
                       END_LIMIT_UPPER_X         |    END_LIMIT_UPPER_X
                               |                 |            |
                               v                 |            v
                         ___  ▮▯▯▯            |           ▮▯▯▯  ____
                         |    ▮ |‡|             |           ▮ |‡|      | 
                         |    ▮ | |             |           ▮ | |      |
                         |       | |             T             | |       |
       END_LIMIT_UPPER_Y |       | |             O             | |       | END_LIMIT_UPPER_Y
                         |      / /   •  •       P       •  •   \ \      |
                         |     / / •  CellN •         •  CellN • \ \     |
                         ‾‾‾‾ | | •   Pos:   •   E   •   Pos:    • | | ‾‾‾
                               \ \•   (X,Yn) •   N   •   (-X,Yn) • / /
                         •  •   \ \•        •    D    •        • / /  •  •                             
                      •        • \ \  •  •       |       •  •   / /•        •                         
                     •          • | |            |             | |•          •                              
                     •          • / /            |             \ \•          • 
                      •        • / /             |              \ \•        •  
                         •  •   / /              |               \ \  •  •     
                               / /               |                \ \            
                 *—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*                                                                    
                                          MIDDLE OF BANDOLIER                                   
                 *—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*—*                                                                 
                                  / /                          \ \       
                                 / /  •  •       |       •  •   \ \      
                                / /•        •    |    •        • \ \     
                               | |•          •   B   •          • | |                            
                               \ \•          •   O   •          • / /                         
                         •  •   \ \•        •    T    •        • / /   •  •                 
                      •  Cell0 • \ \  •  •       T       •  •   / / •  Cell0 •                             
                  __ •   Pos:   • | |            O             | | •   Pos:   • __
                  |  •   (0,0)  • / /            M             \ \ •   (0,0)  •  |
                  |   •        • / /                            \ \ •        •   |
                  |      •  •   | |              E               | |   •  •      |
END_LIMIT_LOWER_Y |             | |              N               | |             | END_LIMIT_LOWER_Y
                  |          ▮ | |              D             ▮ | |            |
                  |          ▮ |‡|              |             ▮ |‡|            |
                  ‾‾‾‾‾‾‾‾‾‾ ▮▯▯▯             |             ▮▯▯▯‾‾‾‾‾‾‾‾‾‾‾‾
                              ^                                 ^
                              |                                 |
                       END_LIMIT_LOWER_X                 END_LIMIT_LOWER_X    
                         <<<---------- Direction of stacking <<<----------

"""

END_LIMIT_LOWER_X = 8
END_LIMIT_UPPER_X = 8

END_CONSTRAINT_INCLUDE_Y_CONSTRAINTS = True # whether to include ▯ limits
END_LIMIT_LOWER_Y = 40
END_LIMIT_UPPER_Y = 40


# Other settings

DISPLAY_CONSTRAINTS = False

# Bando Colours
COLOUR_SILVER = (192,192,192, 255)
COLOUR_MAROON = (	128,0,0, 255)
COLOUR_RED = (255,0,0, 255)
COLOUR_AQUA = (0,255,255, 255)
COLOUR_PURPLE = (128,0,128, 255)
COLOUR_BLUE = (0,0,255, 255)
COLOUR_ORANGE = (255,140,0, 255)
COLOUR_PINK = (255,20,147, 255)
COLOUR_GOLD = (255,215,0, 255)
COLOUR_ALL = [COLOUR_SILVER, COLOUR_MAROON, COLOUR_RED, COLOUR_AQUA, COLOUR_PURPLE, COLOUR_BLUE, COLOUR_ORANGE, COLOUR_PINK, COLOUR_GOLD]

if __name__ == "__main__":
    pass