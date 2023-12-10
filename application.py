from flask import Flask, flash, redirect, render_template, request, url_for
import requests
import json

application = Flask(__name__)       


config = {
 "register_url": "https://zracv2xvfd.execute-api.eu-west-1.amazonaws.com/dev/register",
 "login_url":"https://zracv2xvfd.execute-api.eu-west-1.amazonaws.com/dev/Login",
 "club_url": "https://zracv2xvfd.execute-api.eu-west-1.amazonaws.com/dev/club",
 "clubs_url": "https://zracv2xvfd.execute-api.eu-west-1.amazonaws.com/dev/clubs"
}


person = {"is_logged_in": False, "user_id": "", "password": "", "club_id": ""}


@application.route("/")
def login():
    if person["is_logged_in"] == False:
        return render_template("login.html")
    else: 
        return redirect(url_for('welcome'))

@application.route("/logout", methods=["GET"])
def logout():
    global person
    person = {"is_logged_in": False, "user_id": "", "password": "", "club_id": ""}
    return redirect(url_for('login'))


@application.route("/signup")
def signup():
    return render_template("signup.html")

@application.route("/editteam", methods = ["POST"])
def editteam():
    if(person['is_logged_in']):
        result = getdata()
        print(result.content)
        result = json.loads(result.content)
        return render_template("editteam.html", data=result)
    else:
        return redirect(url_for('login'))
    

@application.route("/home",methods = ["GET"])
def home():
    return redirect(url_for('myteam')) 

@application.route("/viewteams",methods = ["GET"])
def viewteams():
    if(person['is_logged_in']):
        result = getclubs()
        print(result)
        return render_template('viewteams.html',data = result)
    else:
        return redirect(url_for('login'))

def getclubs():
    result = requests.get(config['clubs_url'])
    result = json.loads(result.content)
    return result
    
    
def getdata():
    params = {'club_id':  person['club_id']}
    print(params)
    result = requests.get(config['club_url'], params= params)
    if(result is not None):
        return result
    else:
        return None

@application.route("/deleteteam", methods = ["GET"])
def deleteteam():
    if(person['is_logged_in']):
            params = {'club_id':  person['club_id']}
            result = requests.delete(config["club_url"],json=params)
            return redirect(url_for('welcome'))
    else:
        return redirect(url_for('login'))
        

@application.route("/myteam",methods = ["POST" , "GET"])
def myteam():
    if(person['is_logged_in']):
        if request.method == "POST":        #Only if data has been posted
            result = dict(request.form)        #Get the data
            result['club_id'] = person.get('club_id', {})
            print(result, "from post of myteam")
            try:
                response = requests.post(config['club_url'],json=result)
                result = getdata()
                result = json.loads(result.content)
                return render_template("myteam.html", data = result)
            except:
                #If there is any error, redirect back to login
                return redirect(url_for('myteam'))
        else:
            response = getdata()
            result = json.loads(response.content)
            print("from myteam")
            if(result is not {}):
                return render_template("myteam.html", data = result)  
        result = request.form
        if (result is not None):
            return render_template("myteam.html", data = result)
        else:
            result1 = getdata()
            return render_template("myteam.html", data = result1)
    return redirect(url_for('login'))



@application.route("/welcome")
def welcome():
    if person["is_logged_in"] == True:
        result = getdata()
        if(json.loads(result.content) == {}):
            return render_template("welcome.html")
        else:
            return redirect(url_for("myteam"))
    else:
        return redirect(url_for('login'))


@application.route("/result", methods = ["POST"])
def result():
    if request.method == "POST":        #Only if data has been posted
        result = request.form           #Get the data
        try:
            response = requests.post(config['login_url'],json=result)
            #Try signing in the user with the given information
            #Insert the user data in the global person
            result = json.loads(response.content)
            if(result['Message']=='Failure'):
                return redirect(url_for('login'))
            global person
            person["is_logged_in"] = True
            person["user_id"] = result['user_id']
            person["club_id"] = result['club_id']
            return redirect(url_for('welcome'))
        except:
            #If there is any error, redirect back to login
            return redirect(url_for('login'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('login'))
        
#If someone clicks on register, they are redirected to /register
@application.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":        #Only listen to POST
        result = request.form           #Get the data submitted
        try:
            response = requests.post(config['register_url'],json=result)
            #Add data to global person
            global person
            person["is_logged_in"] = True
            person["user_id"] = response['Item']['user_id']
            person["club_id"] = response['Item']['club_id']
            #Append data to the firebase realtime database
            #Go to welcome page
            return redirect(url_for('welcome'))
        except:
            #If there is any error, redirect to register
            return redirect(url_for('register'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('register'))

if __name__ == "__main__":
    application.run()
