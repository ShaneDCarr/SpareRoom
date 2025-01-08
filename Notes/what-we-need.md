
## Endpoints
    - Get
        > /units 
            -> /{state}
                -> /available
                -> /reserved
                -> /cancelling
                -> /problem
                -> /unavailable

            -> /clients
                - /unit-number
    - Post
        > /units
            -> /unit-number
        > /rent


## What do they need to be able to do
    - rent a unit
        > see available units
            -> Available
        > choose a booking range
            -> 1 day to indefinite
        > choose booking option
            -> Prepay or Recurring
        > choose a payment method
            -> Card or EFT

    - manage payment methods

    - manage unit state (openness)
        > lock and unlock storage units
        > can share state abilities to another user
        > get notified on open state


## What should we be able to do
    - Customer Support
        > see states of units
            -> Available
                - can be booked
            -> Reserved
                - booked by customer
            -> Cancelling
                - if cancelled and in cancellation period
            -> Problem
                - if payment issue
            -> Unavailable
                - due to maintenance
        > should be able to change the state of each unit
