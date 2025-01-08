# Number Code
    - 4 units long
    - number will be unique only to that province and size
        > We can have 2 0001 numbers in the database as long as their province and sizes are different 
            -> `0001_SML_KZN`
            -> `0001_SML_EC0`
            -> `0001_LOC_EC0`

# Size
    - Sizes will be converted to 3 letter abbreviations:
        > Locker -> LOC
        > Small  -> SML
        > Medium -> MED
        > Large  -> LRG

# Province Codes
    - Provinces will be converted to 3 letter abbreviations:
        > Eastern Cape  -> EC0
        > Free State    -> FS0
        > Gauteng       -> GP0
        > KwaZulu-Natal -> KZN
        > Limpopo       -> LP0
        > Mpumalanga    -> MP0
        > Northern Cape -> NC0
        > North-West    -> NW0
        > Western Cape  -> WC0
