1999          Starting year
2002          Last year
FortValley-ST.100      Site file name
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
1            Block # No-till with winter weeds or no cover crop and 0 kg N
2002         Last year
4            Repeats # years
1999         Output starting year
1            Output month
0.083        Output interval
F            Weather choice 
FortValley.wth
1  105  CROP  C6           # Corn for silage
1  105  PLTM
1  288  LAST
1  288  HARV  SIL          # Harvest of corn for silage in October
1  290  CROP  G1WEED        # weeds left growing
1  290  PLTM
2  106  LAST
2  106  HARV  MOW          # CUT weeds and spread in the fields
2  106  CULT  HERB          #
2  106  CULT  ROW          # Check if this CULT event is OK for strip tillage
2  110  CROP  COT          # Two weeks after weeds mowing, plant cotton
2  123  FERT  (0.95P)      # P fertilization during planting
2  123  FERT  (6N)
2  123  IRIG  (0,0,2.5)      # One time irrigation after planting of 2.5 cm
2  123  PLTM
2  165  FERT  (6N)
2  293  LAST
2  293  HARV  G            # Cotton harvest
2  294  CROP  G1WEED       # weeds left growing
2  294  PLTM
3  105  LAST
3  105  HARV  MOW          # CUT weeds and spread in the fields
3  105  CULT  HERB         
3  105  CULT  ROW             # complete CULT event for strip tillage
3  122  CROP  SORG         # Two weeks after weeds mowing, plant cotton
3  122  FERT  (0.95P)      # P fertilization during planting
3  122  FERT  (8N)
3  122  IRIG  (0,0,2.5)    # One time irrigation after planting of 2.5 cm
3  123  PLTM
3  166  FERT  (4N)
3  292  LAST
3  292  HARV  G            # Sorghum harvest
3  293  CROP  G1WEED       # weeds left growing
3  293  PLTM
4  105  LAST
4  105  HARV  MOW          # CUT weeds and spread in the fields
4  105  CULT  HERB         
4  105  CULT  ROW          # Check if this CULT event is OK for strip tillage
4  122  CROP  COT          # Two weeks after weeds mowing, plant cotton
4  122  FERT  (0.95P)      # P fertilization during planting
4  122  FERT  (6N)
4  122  IRIG  (0,0,2.5)      # One time irrigation after planting of 2.5 cm
4  122  PLTM
4  164  FERT  (6N)
4  292  LAST
4  292  HARV G            # Cotton harvest
-999 -999 X

