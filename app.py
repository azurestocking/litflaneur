import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from pyecharts import options as opts
from pyecharts.charts import Graph
from pyecharts.globals import ThemeType
from pyecharts.commons import utils


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///constellation.db")

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Visualize the information in the database"""
    graph_category = [
        {"name": "Claim", "symbol": "circle"},
        {"name": "Reason", "symbol": "circle"},
        {"name": "Evidence", "symbol": "circle"},
        {"name": "Warrant", "symbol": "circle"},
        {"name": "Response", "symbol": "circle"},
    ]

    nodes = db.execute("SELECT * FROM nodes WHERE user_id = ?", session["user_id"])
    links = db.execute("SELECT * FROM links WHERE user_id = ?", session["user_id"])


    c = Graph(
        init_opts=opts.InitOpts(
            theme=ThemeType.WHITE,
        )
    )

    c.add(
        "",
        nodes,
        links,
        graph_category,
        edge_length=30,
        gravity=0.2,
        repulsion=1000,
        is_draggable=True, 
        edge_symbol=None, 
        label_opts=opts.LabelOpts(
            is_show=True,
            color="auto",
        ),
        tooltip_opts=opts.TooltipOpts(
            is_show=True,
            formatter=utils.JsCode("""function(object) {
                console.log(object);
                if ( typeof object.data.summary == 'undefined' ) {
                    return '';
                } else {
                    return object.data.summary + '<br/>' + object.data.author + '\\n' + object.data.date + '. ' + object.data.title +'.';
                }
            }"""),
        ),
    )

    c.set_global_opts(
        title_opts=opts.TitleOpts(
            title="",
        )
    )

    data_plot = c.dump_options()
    return render_template("constellation.html", data_plot=data_plot)


@app.route("/add-node", methods=["GET", "POST"])
@login_required
def add_node():
    """Add new node into the database"""
    if request.method == "POST":
        # Create new node
        name = request.form.get("name")
        category = request.form.get("category")
        summary = request.form.get("summary")
        content = request.form.get("content")
        author = request.form.get("author")
        date = request.form.get("date")
        title = request.form.get("title")
        # Check if name has been taken
        if name and category and summary and content and author and date and title:
            rows = db.execute("SELECT * FROM nodes WHERE name = ?", name)
            if len(rows) != 0:
                return apology("name has been taken", 400)
            # Insert new node into network
            else:
                db.execute("INSERT INTO nodes (user_id, name, category, summary, content, author, date, title) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], name, category, summary, content, author, date, title)
                return redirect("/")
        else:
            return apology("insuffienct information", 400)
    else:
        return render_template("add-node.html")


@app.route("/add-link", methods=["GET", "POST"])
@login_required
def add_link():
    """Add new link into the database"""
    if request.method == "POST":
        # Create new link
        source = request.form.get("source")
        target = request.form.get("target")
        # Insert new link into network
        if source and target:
            db.execute("INSERT INTO links (user_id, source, target) VALUES (?, ?, ?)", session["user_id"], source, target)
            return redirect("/")
        else:
            return apology("insuffienct information", 400)
    else:
        # Display the entries in the database on index.html
        nodes = db.execute("SELECT * FROM nodes")
        return render_template("add-link.html", nodes=nodes)


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """List all nodes created by the user"""
    if request.method == "GET":
        nodes = db.execute("SELECT * FROM nodes")
        return render_template("dashboard.html", nodes=nodes)


@app.route("/search")
@login_required
def search():
    """Search for nodes whose name includes the keyword"""
    nodes = db.execute("SELECT * FROM nodes WHERE name LIKE ?", "%" + request.args.get("q") + "%")
    return render_template("search.html", nodes=nodes) 


@app.route('/manage/<string:name>', methods=['GET'])
def manage(name):
    """Delete the node whose button is clicked"""
    db.execute("DELETE FROM nodes WHERE name = ?", name)
    db.execute("DELETE FROM links WHERE source = ?", name)
    db.execute("DELETE FROM links WHERE target = ?", name)
    return redirect("/")


@app.route("/manifesto")
@login_required
def manifesto():
    """About this project"""
    return render_template("manifesto.html") 


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # If any field is left blank, return an apology
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    # Check for errors
    if request.method == "POST":

        # If any field is left blank, return an apology
        if not request.form.get("username"):
            return apology("must provide username", 400)
        if not request.form.get("password"):
            return apology("must provide password", 400)

        # If password and confirmation don't match, return an apology
        if password != confirmation:
            return apology("password and confirmation must match", 400)

        # If username are already taken, return an apology
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            return apology("username taken", 400)

        # Add new user to the database
        hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Change password"""
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")
        user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # If any field is left blank, return an apology
        if not current_password:
            return apology("must provide current password", 400)
        if not new_password:
            return apology("must provide new password", 400)
        if not confirmation:
            return apology("must confirm new password", 400)
        
        # If password and confirmation don't match, return an apology
        if new_password != confirmation:
            return apology("password and confirmation must match", 400)

        # If current password is incorrect, return an apology
        if not check_password_hash(user[0]["hash"], request.form.get("current_password")):
            return apology("invalid password", 400)
        
        # Generate new hash and update the database
        new_hash = generate_password_hash(new_password)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", new_hash, session["user_id"])
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("password.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run()