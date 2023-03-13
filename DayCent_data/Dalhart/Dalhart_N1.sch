1999          Starting year
2006          Last year
Dalhart_N1.100      Site file name
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
C6            Initial crop
              Initial tree

Year Month Option
1            Block # Continous_corn
2006         Last year
8            Repeats # years
1999         Output starting year
1            Output month
0.083        Output interval
F            Weather choice 
Dalhart.wth
   1  125  CULT F              #Corn 1999
   1  135  CROP C6 
   1  135  PLTM
   1  135  IRIG (1, 0.925F, -1L)  # irrigate to field capacity until end of growing season whenever available water content falls below 0.925
   1  185  FERT (35.3N)
   1  235  CULT ROW 
   1  255  LAST     
   1  255  HARV G
   1  263  CULT H
   2  125  CULT F              #Corn 2000
   2  135  CROP C6
   2  135  PLTM
   2  135  IRIG (1, 0.925F, -1L) 
   2  185  FERT (36.6N)
   2  235  CULT ROW 
   2  255  LAST     
   2  255  HARV G
   2  263  CULT H
   3  125  CULT F              #Corn 2001
   3  135  CROP C6 
   3  135  PLTM
   3  135  IRIG (1, 0.925F, -1L)
   3  185  FERT (29.8N)
   3  235  CULT ROW 
   3  255  LAST     
   3  255  HARV G
   3  263  CULT H
   4  125  CULT F              #Corn 2002
   4  135  CROP C6 
   4  135  PLTM
   4  135  IRIG (1, 0.925F, -1L) 
   4  185  FERT (26.1N)
   4  235  CULT ROW 
   4  255  LAST     
   4  255  HARV G
   5  260  CULT NOTILL         #Wheat 2003
   5  260  CROP W2 
   5  260  PLTM
   5  260  IRIG (1, 0.925F, -1L) 
   5  320  FERT (6.7N)
   6   85  LAST                #Corn 2004    
   6   85  HARV G
   6  135  CROP C6            
   6  135  PLTM
   6  135  IRIG (1, 0.925F, -1L)
   6  185  FERT (20.8N)
   6  255  LAST     
   6  255  HARV G
   7  260  CULT NOTILL         #Wheat 2005
   7  260  CROP W2 
   7  260  PLTM
   7  260  IRIG (1, 0.925F, -1L) 
   7  320  FERT (11.2N)
   8   85  LAST                #Corn 2006    
   8   85  HARV G
   8  136  CROP C6            
   8  136  PLTM
   8  196  FERT (19.2N)
   8  256  LAST     
   8  256  HARV G
-999 -999 X

