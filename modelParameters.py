# BANDOLIER PARAMETERS
"""

        Configuration A         |        Configuration B (note negative x)                 
                                |                  
                                |                   
                     *  *       |       *  *        
                  *  Cell3 *    |    *  Cell3 *     
                 *   Pos:   *   |   *   Pos:   *    
                 *(X,Y2+Y1) *   |   *(-X,Y2+Y1)*    
        *  *      *        *    |    *        *      *  *                             
     *  Cell2 *      *  *       |       *  *      *  Cell2 *                         
    *   Pos:   *                |                *   Pos:   *                              
    *   (0,Y2) *                |                *   (0,Y2) *        
     *        *      *  *       |       *  *      *        *         
        *  *      *  Cell1 *    |    *  Cell1 *      *  *            
                 *   Pos:   *   |   *   Pos:   *                                
                 *   (X,Y1) *   |   *   (-X,Y1)*                             
        *  *      *        *    |    *        *       *  *                 
     *  Cell0 *      *  *       |       *  *       *  Cell0 *                             
    *   Pos:   *                |                 *   Pos:   *                              
    *   (0,0)  *                |                 *   (0,0)  *                         
     *        *                 |                  *        *        
        *  *                    |                     *  *                                  
        
"""

# Number of Iterations
MODEL_NUM_ITERATIONS = 1

# Bandolier cell count
BANDO_CELL_COUNT = 20

# Number of Bandoliers in a module
MODULE_BANDO_COUNT = 3

# Bandolier Designed values (as in CAD)
BANDO_CELL_X = 16 #mm
BANDO_CELL_Y1 = 12 #mm
BANDO_CELL_Y2 = 23 #mm

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