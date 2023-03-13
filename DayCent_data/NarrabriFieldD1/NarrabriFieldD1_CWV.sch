2002          Starting year
2011          Last year
Narrabri-CWV.100      Site file name
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
1            Block                # cotton/wheat/vetch
2011         Last year
3            Repeats # years
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
2  118  CULT  D 
2  140  FERT  (2N)
2  140  CROP  W2                   ## Plant wheat
2  140  PLTM
2  207  FERT  (6N)
2  329  LAST
2  329  HARV  G
2  330  CULT  D
3   54  CROP  VETCH
3   54  PLTM
3  184  LAST
3  184  HARV  MOW
3  185  CULT  D
-999 -999 X

