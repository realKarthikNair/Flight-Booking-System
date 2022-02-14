# backend code to assist main.py and thus manage MySQL database
import mysql.connector as sql
from itertools import islice
from tabulate_module import tabulate
import random

name = " not logged in "

def setup_sql():
    try:
        with open("sql_creds.txt") as data:
            creds = list(islice(data, 2))
            return [creds[0].strip("\n"), creds[1].strip("\n")]
    except:
        



def connect_to_database(username, password):
    global server, flight_booking
    server = sql.connect(host='localhost', user=f'{username}', auth_plugin='mysql_native_password', passwd=f'{password}')  # connecting with sql
    flight_booking = server.cursor()
    try:
        flight_booking.execute("use flight_booking;")  # use database if exists
    except:
        flight_booking.execute('create database flight_booking;')  # create database if first run
        flight_booking.execute("use flight_booking;")

def Chart_DB():
    try:
        query = '''create table chart(Boarding varchar(30),Destination varchar(30),
        Journey_Date date,Departure varchar(5),Arrival varchar(5),Flight_num varchar(6),
        Stops varchar(3),Price varchar(7));'''
        flight_booking.execute(query)
        query = '''create table bookings(Booking_id varchar(4),name varchar(50),
        email varchar(50),Flight_num varchar(6));'''
        flight_booking.execute(query)
        file = open("flight_chart.txt")
        while True:
            try:
                line = file.readline()
                row = line.split(',')
                query = f'''insert into chart values('{row[0]}','{row[1]}','{row[2]}',
                 '{row[3]}' ,'{row[4]}' , '{row[5]}','{row[6]}','{row[7]}')'''
                flight_booking.execute(query)
                server.commit()
            except:
                break
    except:
        pass


def user_info():
    try:
        flight_booking.execute('''create table user_info(name varchar(200),
        email varchar(50),mobile varchar(10),password varchar(200));''')
        name, email, mobile, password = "sample", "sample", "sample", "sample"
        query = f"insert into user_info values ('{name}','{email}','{mobile}','{password}');"
        flight_booking.execute(query)
        server.commit()
    except:
        pass

def check_user(email,index=1):
    flight_booking.execute("select *from user_info;")
    found=False
    for i in flight_booking.fetchall():  # fetchall
        if i[index] == email:
            found=True;return True
    if found==False:
        return False

def mob_number():
    while True:
        num = str(input('\nEnter your 10 digit mobile number: +91 '))
        if check_user(num,2)==True:
            print('''This Mobile number is already registered with us
            Try a different number . ''')
            continue
        if len(num) != 10 or num.isdigit() == False:
            print("Invalid mobile number , please enter a 10 digit mobile number ")
        else:
            return num

 
def password_creation():
    while True:
        password = input("\ncreate a strong password : ")
        check_lower, check_upper, check_digit = 0, 0, 0
        if len(password) < 8:
            print('Password must be at least 8 characters ')
            continue
        for i in password:
            if i.isupper():
                check_upper += 1
            if i.islower():
                check_lower += 1
            if '0' <= i <= '9':
                check_digit += 1
        if check_digit == 0 or check_upper == 0 or check_lower == 0:
            print('Password must contain at least a digit, an upper case character and a lowercase character ')
        else:
            return password
 
def new_user(email):
    print("\nNo existing account found with this email id \n")
    print("creating new Account . . . . \n")
    global name;name = input('\nEnter your name: ')
    mobile = mob_number();password = password_creation()
    query = f"insert into user_info values ('{name}','{email}','{mobile}','{password}');"
    flight_booking.execute(query);server.commit()
    print("Account created successfully \n")
    print(f"Logging you in as {name} \n")
    Chart_DB()

def login(email):
    while True:
        password_check = input("\nenter your password :  ")
        flight_booking.execute("select *from user_info;")
        for i in flight_booking.fetchall():
            if i[1]==email:
                if password_check == i[3]:
                    global name;name = i[0]
                    print(f"logging you as {name} . . . \n")
                    return True
        else:
            print("Incorrect password , try again . \n")


def chart():
    flight_booking.execute("select * from chart;")
    rows = flight_booking.fetchall()
    print(tabulate(rows, headers=["Boarding ", "Destination ","Date","Departure ", "Arrival ", "Flight No. ", "Stops ","Pricek"]))


def search_flight(boarding,destination):
    flight_booking.execute("select * from chart;")
    global flights
    flights=[]
    for i in flight_booking.fetchall():
        if i[0].lower() == boarding and i[1].lower() == destination:
            flights+=[i]
    if len(flights)<1:
        print(f"Currently, no flights available from {boarding} to {destination}")
        choice=input("\nDo you want to see flight chart ? (y/n) ")
        if choice=='y': chart()

def booking_id_storage(): # this table stores ids and ensures that booking ids arent repeated
    try:
        flight_booking.execute("create table id_store(id varchar(4));")
        flight_booking.execute("insert into id_store values('0000');")
    except:
        pass

def generate_booking_id():
    while True:
        # creating a unique booking identifier per ticket
        booking_id = str(random.randint(1000, 9999))
        flight_booking.execute("select * from id_store;")
        data = flight_booking.fetchall()
        for m in data:
            if m[0] == booking_id:
                continue
        else:
            flight_booking.execute(f"insert into id_store values('{booking_id}')")
            server.commit()
            return booking_id


def book(email,flight_num=None):
    Chart_DB()
    boarding = input("\nEnter boarding city : ").lower()
    destination = input("\nEnter destination city : ").lower()
    search_flight(boarding,destination)
    booking_id_storage()
    status = False
    if len(flights)>0:
        print("The following flights are available  . ")
        print(tabulate(flights,headers=["Boarding ", "Destination ", "Date", "Departure ", "Arrival ", "Flight No. ", "Stops ","Price"]))
        num=input("\n Enter last 4 digits of flight number to book : ")
        for i in flights:
            if i[5][2:6]==num:
                while True:
                    seats=int(input("\nenter number of seats :"))
                    try:
                        if seats>10 or seats<1:
                            print("\nYou can only book minimum 1 seat and the maximum 10 seats . ")
                            continue
                    except:
                        print("\nEnter a valid value . ");continue
                    break
                names=[]
                print()
                for j in range(1,seats+1):
                    names+=[input(f"Enter name of passenger {j} : ")]
                price=int(i[7][3:7])
                total_price=price*seats
                pay=input(f"\nProceed to pay Rs {total_price} ? (y/n) : ")
                if pay in ['y','Y']:
                    for name in names:
                        id=generate_booking_id()
                        flight_booking.execute(f"insert into bookings values('{id}','{name}','{email}','{i[5]}')")
                    server.commit()
                    print("\nSuccessfully booked ! ")
                    status=True
        if status!=True:
                print("\nBooking failed :-( \nPlease try again")

def bookings(email):
    choice=input("\nEnter 'show' to see bookings , 'cancel' to get into cancellation window .  ").lower()
    flight_booking.execute(f'''select bookings.Booking_id,bookings.Name,chart.Boarding,chart.Destination,
    chart.Journey_Date,chart.Departure,chart.Arrival,chart.Flight_num from bookings,chart 
    where email='{email}' and bookings.Flight_num=chart.Flight_num ''')
    bookin=flight_booking.fetchall()
    if bookin==[]:
        print("\nNo bookings found . ")
    else:
        print(f"\nBookings by user {name} ({email}) : ")
        print(tabulate(bookin,headers=["Booking_id", "Name", "Boarding", "Destination", "Journey Date", "Departure", "Arrival","Flight No."]))
        if choice=='cancel':
            id=input("\nEnter booking id to cancel : ")
            cancel_status = 0
            for i in bookin:
                    if i[0]==id:
                        cancel_status += 1
                        break
            if cancel_status>0:
                flight_booking.execute(f"delete from bookings where Booking_id='{id}' and email='{email}';")
                server.commit()
                print("\ncancellation successful ,a part of money will be refunded according to T&C  .")
                cancel_status=True
            else:
                print("\nWrong booking id entered . please try again ")
                bookings(email)

def account(email):
    flight_booking.execute(f"select name,email,mobile from user_info where email='{email}' ;")
    info=flight_booking.fetchall()
    print(tabulate(info,headers=["Name","Email","mobile no."]))
    choice=input("\nEnter 'edit' to edit Account info , 'logout' to log out . ").lower()
    if choice=="edit":
        while True:
            new_num = str(input("\nEnter new mobile number ('enter' to skip) : +91 "))
            if check_user(new_num,2)==True:
                print("\nmobile number already exists ")
                return "repeat"
            if new_num!="":
                if len(new_num) != 10 or new_num.isdigit() == False:
                    print("\nInvalid mobile number , please enter a 10 digit mobile number ");continue
                flight_booking.execute(f"update user_info set mobile='{new_num}' where email='{email}' ")
                server.commit()
                print("\nSuccessfully updated ! ")
            new_email=input("\nEnter new email/username address ('enter' to skip): ")
            if check_user(new_email)==True:
                print("\nEmail/username already exists ")
                return "repeat"
            if new_email!="":
                flight_booking.execute(f"update user_info set email='{new_email}' where email='{email}' ")
                server.commit()
                flight_booking.execute(f"update bookings set email='{new_email}' where email='{email}' ")
                server.commit()
                print("\nSuccessfully updated ! ");return new_email
            if new_email=="":
                break
    if choice=="logout":
        print("\nSuccessfully logged out ! ")
        return "logout"

