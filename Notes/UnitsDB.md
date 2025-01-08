## Primary Key
    - unit_id (string hash) -> thinking something like `number_size_provinceAbreviation`
                            -> See `ConventionsForUnitsDB.md`

## Attributes
    - size
        > locker
        > small
        > medium
        > large
    - location
    - state
        > state: available
            -> details: {
                - price :int
                }
        > state: reserved
            -> details : {
                - end_date: string
                - renter: email
                - shared: bool
                - shared_with: [
                        email,
                        email
                    }
                - price: int
                - is_open: bool
                }

