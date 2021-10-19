# SCORING INQUILINOS
#### Video Demo:  <URL https://youtu.be/rtoQ7l8mvuY>
#### Description:

### This project uses Django as Framework.
## Files:
### The folder 'inquilinoscore':
* has the settings where is incorporated 'score' as an INSTALLED_APPS.
* has the app 'score' as the default path.

### The folder 'media':
* Has all the profile photos of the users.

### The folder 'score' is the app folder:
* Inside the 'static' folder has:
    * A Javascript file.
    * A CSS file.
    * A folder called media where has the default photo that displays when a users doesn't upload a profile image.

* Inside the 'templates' folder has the following files:
    * Layout.html
    * Index.html that it's used to display the list of users, the list of renters and the search page.
    * Login.html that displays the login view.
    * Password.html that displays the view to change the password of the user logged-in.
    * Profile.html that displays the view of each users profile.
    * Register.html that displays the register view.
    * update.html that displays the view to upload the profile of the user logged-in.

* Admin.py allows the super-admin-user to make changes into the models created.
* models.py contains all the models that allows the server to interact with the database.
* urls.py links the paths to the views.
* util.py has a couple of functions I create in order to make more legible the code into the view.py file.
* views.py has all the linked to a certain path into the urls.py.


### the manage.py is the file that control all the web page.
### the requirements.txt is the file that contains all the required programas.


# ¿How to run the app?
Use the commnad-line: 'pip install -r requirements-txt' to install all the requirements.
Use the command-line: 'python manage.py runserver' to run the app.


## Why this project?
In my country, Argentina, we have a problem with people who want to rent an aparment or a house. They need to make an attachment of their houses or their cars as a warranty for the owner. The problem is that they haven't a house of their own or this proccess costs money they don't have.
Also, the price of the rent has increse because of the bad regulation of the rents in Argentina.
So, my idea is to identify those people that always pays rent in order to make less expensive their experience looking for an apartment. As the bank has a credit history of their customers, this scoring of renters looks the same: identify those who are good customers.


## My web page, Scoring Inquilinos, is a web where owners can score their renters. This allows the renters to have a reputation that improves their chances to rent an aparment.

### The web allows people to:
* register as owner, renter or both
* change their password
* update their profile
* make a description of their profile
* upload an image of theirself
* if you are a renter you can allow a owner to score you
* if you are a owner you can score a renter
* when you score a renter you can make comments

### The web page:
* Has an option to show a list of users (owners, renters, or those who are neither owner neither renter) and an option to show a list of only renters.
* Has an option to search for a particular user if you have his/her username, name, lastname or dni (Number of indentification here in Argentina).
* Has an option to enter to your own profile if you are logged-in.
* Displays the profile of the user if you click on his/her display-box.
* Shows al the data of the users, including a description, if he/she is a owner, a renter, both or neither owner or renter. Also, displays the photo the user selected as a profile photo.
* if the user is a renters shows the average score and all the scoring that other people made, including comments.
* if you are a owner and enter you enter into the profile of a renter that you already scored, it displays the score number you give him/her.