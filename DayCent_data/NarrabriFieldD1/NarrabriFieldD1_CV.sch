2002          Starting year
2011          Last year
Narrabri-CV.100      Site file name
0             Labeling type
-1            Labeling year
-1.00         Microcosm
-1            CO2 Systems
-1            pH effect
-1            Soil warming
0             N input scalar option (0 or 1)
0             OMAD scalar option (0 or 1)
0             Climate scalar option
1             Initial system
COT            Initial crop       
              Initial tree

Year Month Option
1            Block                 # Cotton with vetch
2011         Last year
2            Repeats # years
2002         Output starting year
1            Output month
0.083        Output interval
F            Weather choice 
Narrabri.wth
1  288  CROP  COT
1  288  PLTM
1  290  IRIG  (1, 0.925F, -1L)   ## Irrigate to field capacity until end of growing season whenever AWC falls bellow 0.925  
2  118  LAST
2  118  HARV  G
2  119  CULT  D
2  135  CROP  VETCH        ## Plant vetch crop  
2  135  PLTM
2  255  LAST               ## Last day of growth
2  256  HARV  MOW          ## CUT vetch and spread in the fields
2  256  CULT  D            ## Incorporate vetch residues
-999 -999 X

