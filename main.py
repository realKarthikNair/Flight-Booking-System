from db_manage import *

running_status = False

try:
    connect_to_database()
    user_info()
    running_status = True
    print('Welcome to CRK Flight Booking System ', end="\n\n")
except:
    print('The booking system is down currently, please try again later ')

def start_up():
    if running_status == True:
        email = str(input("Enter your email for sign-in/sign-up:  ")).lower()
        if email!="" and ('@' in email) and (".com" in email):
            if check_user(email)==True:
                login(email)
            if check_user(email)==False:
                new_user(email)
            return email
        else:
            print("enter a valid email id .")
            start_up()

email=start_up()
options = {"chart": "for seeing flight chart", "book": "to book flights", "bookings": "to see bookings and ticket cancellation",
           "account": "to view/edit account info and logout . "}

while True:
    print()
    for i in options.keys():
        print(f"    enter {i} {options[i]} ")
    print("    enter exit to exit")
    option = input("\n [enter here] : ").lower()
    if option in options.keys():
        if option == "chart":
            chart()
        elif option == "book":
            book(email)
        elif option == "bookings":
            bookings(email)
        elif option == "account":
            a=account(email)
            if a=="repeat":
                a=account(email)
            if a == "logout":
                email = start_up()
            elif a!=None:
                email=a
    elif option == "exit":
        print("Thank you for using CRK Flight Booking system , see you soon ! ")
        break
    else:
        print('invalid input , try again  .')

