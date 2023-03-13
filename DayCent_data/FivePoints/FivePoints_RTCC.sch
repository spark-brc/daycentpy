1999          Starting year
2015          Last year
FP_RTCC.100      Site file name
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
MXNNL         Initial crop        
              Initial tree

Year Month Option
1            Block # cover crops+tomato
2000         Last year
2            Repeats # years
1999         Output starting year
1            Output month
0.083        Output interval
F            Weather choice 
FivePoints.wth
   1  298  CROP  MXNNL               ## Cover crop
   1  298  PLTM                      ## First day of growing
   1  299  IRIG (0,0,10)             ## Year1999 single daily irrigation of 10 cm
   2   75  LAST                      ## Last day of growing           
   2   75  HARV MOW                  ## MOW cover crop 
   2   76  CULT HERB                 ## Herbicide
   2   98  CROP  JTOM                ## Plant tomato
   2   98  PLTM                      ## First day of growing
   2   98  FERT  (0.98N)             ## N fertilizer (g m2)
   2   98  FERT  (4.64P)             ## P fertilizers (g m2)
   2   99  IRRI  (17C)               ## Year2000 month-long irrigation of 17 cm (4.25 cm each week)      
   2  128  FERT  (5.13N)             ## N fertilizer (g m2)
   2  130  IRRI  (18C)               ## Year2000 month-long irrigation of 18 cm (4.25 cm each week)
   2  162  IRRI  (18C)               ## Year2000 month-long irrigation of 18 cm (4.25 cm each week)
   2  193  IRRI  (18C)               ## Year2000 month-long irrigation of 18 cm (4.25 cm each week)
   2  228  LAST                      ## Last day of tomato growth
   2  228  HARV  G                   ## Tomato harvest
   2  299  CROP  MXNNL               ## Plant cover crop
   2  299  PLTM                      ## First day of cover crop
-999 -999 X
2            Block # cover crops+tomato
2009         Last year
2            Repeats # years
2001         Output starting year
1            Output month
0.083        Output interval
C            Weather choice 
   1   75  LAST                      ## Last day of growth
   1   75  HARV  MOW                 ## MOW cover crops
   1   76  CULT  HERB                ## Herbicide
   1  105  CROP  COT                 ## Plant cotton
   1  105  PLTM                      ## First day of cotton
   1  105  FERT  (2.4N)              ## N Fertilizer
   1  105  FERT  (4.64P)             ## P fertilizer
   1  106  IRRI  (10.1C)             ## month-long irrigation of 10.1 cm (2.52cm each week)      
   1  137  IRRI  (10.1C)             ## month-long irrigation of 10.1 cm (2.52cm each week)
   1  160  FERT  (2.4N)              ## N Fertilizer             
   1  160  FERT  (11.6P)             ## P fertilizer
   1  169  IRRI (10.1C)              ## month-long irrigation of 10.1 cm (2.52cm each week)          
   1  200  IRRI (10.1C)              ## month-long irrigation of 10.1 cm (2.52cm each week)           
   1  232  IRRI (10.1C)              ## month-long irrigation of 10.1 cm (2.52cm each week)          
   1  264  IRRI (10.1C)              ## month-long irrigation of 10.1 cm (2.52cm each week) 
   1  295  LAST                      ## Last day of growth
   1  295  HARV  G                   ## Harvest cotton
   1  298  CROP  MXNNL               ## Plant cover crops
   1  298  PLTM                      ## First day of growing
   2   75  LAST                      ## Last day of growth
   2   75  HARV  MOW                 ## MOW cover crops   
   2   76  CULT  HERB                ## Herbicide
   2   98  CROP  JTOM                ## Plant tomato
   2   98  PLTM                      ## First day of growing
   2   98  FERT  (0.98N)             ## N fertilizer
   2   98  FERT  (4.64P)             ## P fertilizer
   2   99  IRRI  (17C)               ## month-long irrigation of 17 cm (4.25 cm each week) 
   2  128  FERT  (5.13N)             ## N fertilizer
   2  130  IRRI  (18C)               ## Year2000 month-long irrigation of 18 cm (4.25 cm each week)
   2  162  IRRI  (18C)               ## Year2000 month-long irrigation of 18 cm (4.25 cm each week)
   2  193  IRRI  (18C)               ## Year2000 month-long irrigation of 18 cm (4.25 cm each we
   2  228  LAST                      ## Last day of growth
   2  228  HARV  G                   ## Tomato harvest                  
   2  299  CROP  MXNNL               ## Plant cover crop
   2  299  PLTM                      ## First day of growing
-999 -999 X
3            Block # CC(cover crop, improved to increase biodiversity of species)+ tomato + cotton  
2011         Last year
1            Repeats # years
2010         Output starting year
1            Output month
0.083        Output interval
C            Weather choice
   1   75  LAST                      ## Last day of growth
   1   75  HARV  MOW                 ## MOW cover crops
   1   76  CULT  HERB
   1  105  CROP  COT                 ## Plant cotton
   1  105  PLTM                      ## First day of cotton
   1  105  FERT  (2.4N)              ## N Fertilizer
   1  105  FERT  (4.64P)             ## P fertilizer
   1  106  IRRI  (10.1C)              ## month-long irrigation of 10.1 cm (2.52cm each week)      
   1  137  IRRI  (10.1C)              ## month-long irrigation of 10.1 cm (2.52cm each week)
   1  160  FERT  (2.4N)              ## N Fertilizer             
   1  160  FERT  (11.6P)             ## P fertilizer
   1  169  IRRI  (10.1C)              ## month-long irrigation of 10.1 cm (2.52cm each week)          
   1  200  IRRI  (10.1C)              ## month-long irrigation of 10.1 cm (2.52cm each week)           
   1  232  IRRI  (10.1C)              ## month-long irrigation of 10.1 cm (2.52cm each week)          
   1  264  IRRI  (10.1C)              ## month-long irrigation of 10.1 cm (2.52cm each week) 
   1  295  LAST                      ## Last day of growth
   1  295  HARV  G                   ## Harvest cotton
   1  298  CROP  MXNLL               ## Plant cover crops
   1  298  PLTM                      ## First day of growing
   1  299  IRIG  (0,0,5)             ## Single irrigation of 5 cm to cover crops
-999 -999 X
4            Block # CC(cover crop)+ tomato + cotton
2015         Last year
2            Repeats # years
2012         Output starting year
1            Output month
0.083        Output interval
C            Weather choice 
   1   75  LAST                      ## Last day of growth
   1   75  HARV  MOW                 ## MOW cover crops
   1   76  CULT  HERB                ## Herbicide
   1  105  CROP  COT                 ## Plant cotton
   1  105  PLTM                      ## First day of cotton
   1  105  FERT  (2.4N)              ## N Fertilizer
   1  105  FERT  (4.64P)             ## P fertilizer
   1  106  IRRI  (10.1C)             ## month-long irrigation of 10.1 cm (2.52cm each week)      
   1  137  IRRI  (10.1C)             ## month-long irrigation of 10.1 cm (2.52cm each week)
   1  160  FERT  (2.4N)              ## N Fertilizer             
   1  160  FERT  (11.6P)             ## P fertilizer
   1  169  IRRI  (10.1C)             ## month-long irrigation of 10.1 cm (2.52cm each week)          
   1  200  IRRI  (10.1C)             ## month-long irrigation of 10.1 cm (2.52cm each week)           
   1  232  IRRI  (10.1C)             ## month-long irrigation of 10.1 cm (2.52cm each week)          
   1  264  IRRI  (10.1C)             ## month-long irrigation of 10.1 cm (2.52cm each week) 
   1  295  LAST                      ## Last day of growth
   1  295  HARV  G                   ## Harvest cotton
   1  298  CROP  MXNLL               ## Plant cover crops
   1  298  PLTM                      ## First day of growing
   1  299  IRIG  (0,0,5)             ## Single irrigation of 5 cm to cover crops
   2   75  LAST                      ## Last day of growth
   2   75  HARV  MOW                 ## MOW cover crops 
   2   76  CULT  HERB                ## Herbicide         
   2   98  CROP  JTOM                ## Plant tomato
   2   98  PLTM                      ## First day of growing
   2   98  FERT  (0.98N)             ## N fertilizer
   2   98  FERT  (4.64P)             ## P fertilizer
   2   99  IRRI  (17C)               ## month-long irrigation of 17 cm (4.25 cm each week)                 
   2  128  FERT  (5.13N)             ## N fertilizer
   2  130  IRRI  (18C)               ## Year2000 month-long irrigation of 18 cm (4.25 cm each week)
   2  162  IRRI  (18C)               ## Year2000 month-long irrigation of 18 cm (4.25 cm each week)
   2  193  IRRI  (18C)               ## Year2000 month-long irrigation of 18 cm (4.25 cm each week)
   2  228  LAST                      ## Last day of growth
   2  228  HARV  G                   ## Tomato harvest                   
   2  299  CROP  MXNLL               ## Plant cover crop
   2  299  PLTM                      ## First day of growing
-999 -999 X 