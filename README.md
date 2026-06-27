# alumni-club

Web project

google cloud > Computer Engines > VM Instances

locally: 
    open http://35.208.59.90/
    curl -v --max-time 10 35.208.59.90
    curl ifconfig.me

in VM/cloud shell:
    gcloud compute firewall-rules list --format=json
    gcloud compute firewall-rules update default-allow-http --source-ranges=0.0.0.0/0
    gcloud compute firewall-rules update default-allow-http --source-ranges=208.127.57.164/32

in VM:
    /home/nikola_dey_georgiev/alumniconf/firewall/set-firewall.sh
    /home/nikola_dey_georgiev/alumniconf/firewall2/set-firewall.sh 208.127.57.158
    /home/nikola_dey_georgiev/alumniconf/firewall2/reset-firewall.sh 
    # shows all ports that the VM is currently listening on
    ss -tlnp 
    # shows all ports explicitly allowed by the firewall-rules
    gcloud compute firewall-rules list --format="table(name,allowed,sourceRanges)"
    # restarts server
    /home/nikola_dey_georgiev/alumniconf/restart.sh


NOTES

  A small heads-up on #10: if the user's PHP install has display_errors=On and a fatal happens before respond() runs (e.g. a parse error in a require_once'd file, or an OOM), the
  catch won't help — those are caught only by a process-level set_exception_handler/register_shutdown_function. The closures protect everything that's reachable from inside a request
  handler, which is what 99% of "stack trace leaked to user" scenarios are.


 sudo chown -R www-data:www-data ~/alumni-club/uploads/

Database Layer. Contains one table users with information:

USERS:  
  id              INT AUTO_INCREMENT PRIMARY KEY,
  name            VARCHAR(127)
  email           VARCHAR(255)
  password_hash   VARCHAR(255)
  graduation_year SMALLINT,
  field_of_study  VARCHAR(127)
  current_role    VARCHAR(127)
  company         VARCHAR(127)
  location        VARCHAR(127) 
  bio             VARCHAR(127) 
  profile_picture VARCHAR(255) 



id is a unique identifier
name is a list of words of leght not greater than …
email is a unique email …
graduation year is a year between 1900 and 2100 …
companyrole is a list of words of lenght not greater than …
company is a list of words of lenght not greater than …
bio is a list of words of lenght not greater than …
profile picture is a viable image file of type .png and size in bytes on server not greater than …
The set [name, email, graduation_year, fieldofstudy, companyrole, company, location, bio, profile picture] is called public user data
The set [password] is called private user data
The set [id] is called system user data
A person can register as user
Registered user can log as user
Logged user can see his user data
Logged user can modify any field in his private or public data
Logged user can delete all of his user data from the system permanently
Logged user can log out
Logged user can see all approved registered users’ public data


authentication
processing images in post/patch
exposing img/<file>


index.html
accordion: registration form 
accordion: login form
accordion: logout button
accordion: user data 
accordion: edit profile
accordion: all users
accordion: search users
accordion: create event
accordion: all events
accordion: search events

documenting project




Tests

1. Registration
    1. Success
        1. Minimal smoke test- checks for success
        2. Maximal smoke test - checks for success
    2. Fail
        1. Name
            1. empty
            2. 128c
            3. non-ascii
        2. Email
            1. empty
            2. invalid pattern
            3. 128c
            4. non-ascii
        3. password
            1. empty
        4. other string fields
            1. 128c
            2. non ascii
        5. PPicture
            1. invalid format
            2. file size too big


2. Component
    1. Scenario 1
        1. Register
        2. Login
        3. Logout
    2. Scenario 2
        1. Register
        2. Login
        3. Delete
    3. Scenario 3
        1. Register 
        2. Login 
        3. Get
    4. Scenario 4
        1. Register
        2. Login 
        3. GetAll
    5. Scenario 5
        1. Register 
        2. Login 
        3. Edit
        4. Get



