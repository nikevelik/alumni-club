# System requirements


# Shorthands
1. User is any entity that can establish internet connection with the system. 
2. RUser is a registered user. 
3. LUser is a logged user.
4. Valid string means a sequence of up to 127 ASCII-only characters
5. Userfilter is a non-empty valid string pattern for matching substrings of user emails
6. Event filter is a non empty valid string patter for matching substrings of event names

# Registration
1. Any user can register at least once in the system
2. Registration requires a valid (RFC-5322-formatted valid string) email
3. Registration requires a valid (non-empty valid string) password
4. Registration has optional input (any valid valid string) name
5. Registration has optional input (1900-2100 integer) graduation year
6. Registration has optional input (any valid string) field of study
7. Registration has optional input (any valid string) current roke
8. Registration has optional input (any valid string) location
9. Registration has optional input (any valid string) bio
10. Registration has optional input (less than 65536 bytes file of type image) profile picture
11. Upon registration, when user enters invalid field, an indication of the problem and the affected field is shown.
12. Upon successful registration, provided input is stored.
13. Upon successful registration, provided password is encrypted and/or hashed with an algorithm 
14. Upon successful registration, an indication is shown

# Login

1. RUser can login
2. Login requires email and password
3. Upon login, when invalid email and/or password is provided, an indication of the problem is shown
4. Upon successful login, an indication is shown
5. Upon successful login, a cookie might be initialized

# Logout
1. LUser can log out
2. Upon successful logout, indication is shown

# User Deletion
1. LUser can delete the input stored for their account
2. Deletion includes unregistration and logout
3. Upon successful deletion, indication is shown

# User Editing
1. LUser can modify the stored input field types, provided upon registration
2. Upon successful edit, indication is shown

# Users Preview
1. LUser can view provided emails, names, gyears, fostudies, croles, locations, bios, ppictures of all the users in the system
2. LUser can view provided ... of users that match a userfilter

# Create event
1. LUser can create an event
2. Event creation requires a valid date 
3. Event creation requires a non-empty valid string name
4. Event creation has an optional input valid string description
5. Upon event creation, if a field is invalid, an indication of the problem and the affected field is shown.
6. Upon successful event creation, an indication is shown

# Delete event
1. LUser can delete event, created by him
2. Upon successful deletion, an indication is shown

# Events preview
1. LUser can view provided name, date, details of all the event in the system
2. LUser can view provided ... of events that match a eventfilter