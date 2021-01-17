# ZoomCount
Unfortunately, I learned from deploying this app that PyAutoGui does not work on a web app, since it runs on the server.  
However, for those still interested in trying this app out, the app should work fine on the localhost following these steps:

__Set up__
1) Clone the repository
2) Go to the local directory
2) Create a virtual env (optional, but recommended); install packages from requirements.txt
3) Create the main.db file from app:
  - in a console, type: `py` (to run python)
  `from app import db`
  `db.create_all()`
  `Ctrl+z` (to exit python)
  
__Using the App__
1) Run app.py
2) Go to the localhost link listed in the console (should be something like: Running on http://127.0.0.1:5000/ (Press CTRL+C to quit))
3) Once on the site, create an account, and follow the instructions listed on the home page.
4) Enjoy!

If you'd like to try tracking your zoom data and would like to send it to me, or just have any questions about the app, email me at [tylerwu2222@g.ucla.edu](mailto:tylerwu2222@g.ucla.edu).
For the foreseeable future, this project is discontinued. 
