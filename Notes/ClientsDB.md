## Primary Key
    - client-email

## Attributes
    - first_name 
    - Last_name
    - payment_method
    - location
    - phone_number
    - units
        > unit_id (int hash)
        > unit_billing_options (int) {
                                        0 - Recurring Monthly
                                        1 - Recurring Yearly
                                        2 - Pre_pay
                                    }
        > accrued_cost_for_unit (int)
        > shared (bool)
        > shared_with (emails)
        > end_date (string) {
                                dd/mm/yyyy
                                indefinite 
                            }

