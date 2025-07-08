# Data Cleaning Summary

## Cleaning Actions
- Handled missing values in 'Name' with mode
- Handled missing values in 'Age' with mode
- Handled missing values in 'Email' with mode
- Handled missing values in 'SignupDate' with mode
- Handled missing values in 'Country' with mode
- Handled missing values in 'PurchaseAmount' with mode
- Removed 5 duplicate rows
- Standardized column names to snake_case
- Checked and fixed data types for 'customerid'
- Checked and fixed data types for 'name'
- Checked and fixed data types for 'age'
- Checked and fixed data types for 'email'
- Checked and fixed data types for 'signupdate'
- Checked and fixed data types for 'country'
- Checked and fixed data types for 'purchaseamount'
- Normalized text in 'customerid'
- Normalized text in 'name'
- Normalized text in 'age'
- Normalized text in 'email'
- Normalized text in 'signupdate'
- Normalized text in 'country'
- Deduplicated 89 text entries in 'email' using fuzzy matching
- Parsed 'signupdate' as datetime using format %Y-%m-%d
- Scaled 'purchaseamount' using min-max scaling
