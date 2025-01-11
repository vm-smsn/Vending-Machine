# Vince Michael J. Samson | ID:04-24-0147
# Assessment 2: Vending Machine
# 11/25/2024

'''
Welcome To Kel's Vending program!!!

'''

import sqlite3
import pyttsx3
import time
import random

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

# Connect to the database
db = sqlite3.connect('C:/Users/vince/.spyder-py3/Vending Machine.db')

# Function to display the snack menu
def DisplayMenu():
    query = "SELECT * FROM product;"
    item_information = db.execute(query)
    print(f"\n{'-'*28}MENU{'-'*28}")
    print(f"{'Code':<10}{'Name':<32}{'Price':<13}{'Stock':<0}")
    print(f"{'-'*60}")
    for item in item_information:
        print(f"{item[0]:<10}{item[1]:<32}AED{item[2]:<10.2f}{item[3]:<10}")
    print(f"{'-'*60}")

# Function to update stock
def UpdateStock(code, quantity):
    query = "UPDATE product SET Stock = Stock - ? WHERE Code = ?;"
    db.execute(query, (quantity, code))
    db.commit()

# Function to restock the vending machine dynamically
def RestockMachine():
    code = input("Enter the product code to restock: ")
    quantity = int(input("Enter the quantity to restock: "))
    query = "UPDATE product SET Stock = Stock + ? WHERE Code = ?;"
    db.execute(query, (quantity, code))
    db.commit()
    print(f"\nThe product {code} has been restocked with {quantity} items.")
    speak(f"The product {code} has been restocked with {quantity} items.")

# Inventory alert when stock is low
def InventoryAlert():
    query = "SELECT Code, Name, Stock FROM product WHERE Stock <= 3;"
    low_stock_items = db.execute(query).fetchall()
    if low_stock_items:
        for item in low_stock_items:
            print(f"Alert: {item[1]} (Code: {item[0]}) is running low. Stock: {item[2]}")
            speak(f"Alert: {item[1]} is running low. Stock: {item[2]}")
    else:
        print("All items are sufficiently stocked.")
        speak("All items are sufficiently stocked.")

# Function to create user accounts (for simplicity, we will use a basic dictionary to simulate user data)
users = {}

# Function to log in or create a new account
def login_or_create_account():
    print("Welcome! Please log in or create an account.")
    speak("Welcome! Please log in or create an account.")
    action = input("Enter 'LOGIN' to log in or 'CREATE' to create a new account: ").upper()

    if action == "CREATE":
        username = input("Enter a new username: ")
        if username in users:
            print("Username already exists. Please try a different one.")
            speak("Username already exists. Please try a different one.")
            return None
        else:
            password = input("Enter a password: ")
            users[username] = {"password": password, "loyalty_points": 0}
            print(f"Account created for {username}!")
            speak(f"Account created for {username}!")
            return username
    elif action == "LOGIN":
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        if username in users and users[username]["password"] == password:
            print(f"Welcome back, {username}!")
            speak(f"Welcome back, {username}!")
            return username
        else:
            print("Invalid credentials. Please try again.")
            speak("Invalid credentials. Please try again.")
            return None
    else:
        print("Invalid action. Please try again.")
        speak("Invalid action. Please try again.")
        return None

# Function to log sales data
def LogSale(cart, total_cost, username):
    query = "INSERT INTO sales (item_code, quantity, total_cost, username) VALUES (?, ?, ?, ?);"
    for code, name, price, quantity in cart:
        db.execute(query, (code, quantity, total_cost, username))
    db.commit()

# Main vending machine loop
while True:
    cart = []  # Holds selected items and quantities
    username = login_or_create_account()
    if username is None:
        continue  # Restart if login fails
    
    DisplayMenu()
    speak("Welcome to Kel's Vending. Start selecting items.")

    while True:
        selected_item = input("\nPlease select an item to buy. (or type 'DONE' to proceed to checkout, '0' to exit): ").upper()
        if selected_item == '0':
            print("Thank you for using Kel's Vending. \nHAVE A GREAT DAY!")
            speak("Thank you for using Kel's Vending. Have a great day!")
            exit()

        if selected_item == 'DONE':
            if not cart:
                print("Your cart is empty. Please add at least one item.")
                speak("Your cart is empty. Please add at least one item.")
            else:
                break

        query = "SELECT * FROM product WHERE Code = ?;"
        cursor = db.execute(query, (selected_item,))
        snack = cursor.fetchone()

        if snack:
            name, price, stock = snack[1], snack[2], snack[3]
            if stock > 0:
                print(f"\nYou selected: {name} - AED{price:.2f}")
                speak(f"You selected {name}. The price is {price} Dirhams.")
                print(f"Stock available: {stock}")
                speak(f"There are {stock} {name} available at the moment.")
        
                while True:  # Loop until a valid quantity is entered
                    try:
                        speak(f"How many {name} would you like to buy?")
                        quantity = int(input(f"How many {name} would you like to buy? "))
                        if quantity > stock:
                            print(f"Sorry, we only have {stock} {name} in stock.")
                            speak(f"Sorry, we only have {stock} {name} in stock.")
                            restock = input("Would you like to restock this item? (yes/no): ").strip().lower()
                            if restock == 'yes':
                                print("Restocking the vending machine. Please wait 10 seconds...")
                                speak("Restocking the vending machine. Please wait 10 seconds.")
                                time.sleep(10)
                                RestockMachine()  # Allow the user to restock the item
                                snack = db.execute("SELECT * FROM product WHERE Code = ?", (selected_item,)).fetchone()  # Re-fetch snack data after restocking
                                print(f"Restocking completed. {name} is now available again.")
                                speak(f"Restocking completed. {name} is now available again.")
                                # Recheck stock after restocking and allow to continue
                                if snack[3] >= quantity:
                                    print(f"You can now purchase {quantity} {name}.")
                                    speak(f"You can now purchase {quantity} {name}.")
                                    break  # Exit the loop after successful purchase
                                else:
                                    print(f"Unfortunately, we still don't have enough {name} in stock.")
                                    speak(f"Unfortunately, we still don't have enough {name} in stock.")
                            else:
                                print("You chose not to restock. Please choose a different quantity.")
                                speak("You chose not to restock. Please choose a different quantity.")
                        elif quantity <= 0:
                            print("Invalid quantity. Please try again.")
                            speak("Invalid quantity. Please try again.")
                        else:
                            cart.append((selected_item, name, price, quantity))
                            print(f"Added {quantity} {name} to your cart.")
                            speak(f"Added {quantity} {name} to your cart.")
                            break  # Exit the loop after valid input
                    except ValueError:
                        print("Invalid input. Please enter a valid quantity.")
                        speak("Invalid input. Please enter a valid quantity.")
            else:
                print(f"Sorry, {name} is out of stock.")
                speak(f"Sorry, {name} is out of stock.")
                restock = input("Would you like to restock the vending machine? (yes/no): ").strip().lower()
                if restock == 'yes':
                    print("Restocking the vending machine. Please wait 10 seconds...")
                    speak("Restocking the vending machine. Please wait 10 seconds.")
                    time.sleep(10)
                    RestockMachine()  # Allow the user to restock the item
                    snack = db.execute("SELECT * FROM product WHERE Code = ?", (selected_item,)).fetchone()  # Re-fetch snack data after restocking
                    print("You can now start again.")
                    speak("You can now start again.")
        else:
            print("Item is not available in Kel's Vending. Please try again.")
            speak("Item is not available in Kel's Vending. Please try again.")



       # Checkout
    total_cost = sum(item[2] * item[3] for item in cart)
    print("\nYour cart:")
    for code, name, price, quantity in cart:
        print(f"{quantity} x {name} - AED{price:.2f} each")
    print(f"Total cost: AED{total_cost:.2f}")
    speak(f"Your total cost is {total_cost} Dirhams.")

    total_cost = sum(item[2] * item[3] for item in cart)
print("\nYour cart:")
for code, name, price, quantity in cart:
    print(f"{quantity} x {name} - AED{price:.2f} each")
print(f"Total cost: AED{total_cost:.2f}")
speak(f"Your total cost is {total_cost} Dirhams.")

while True:
    try:
        user_bill = float(input("Enter your bill amount (AED): "))
        if user_bill < total_cost:
            print(f"Insufficient funds. You need at least AED{total_cost:.2f}.")
            speak(f"Insufficient funds. You need at least {total_cost} Dirhams.")
        else:
            change = user_bill - total_cost
            print(f"Your change is: AED{change:.2f}")
            speak(f"Your change is {change} Dirhams.")

            print("Processing your purchase...")
            speak("Processing your purchase.")

            # Update stock for each item in the cart
            for code, name, price, quantity in cart:
                UpdateStock(code, quantity)

            # Log the sale for the user account
            LogSale(cart, total_cost, username)

            # Update loyalty points dynamically
            loyalty_points = random.randint(1, 5)  # Earn random points between 1 and 5
            if username in users:
                users[username]["loyalty_points"] += loyalty_points

            print(f"You've earned {loyalty_points} loyalty points! Total: {users[username]['loyalty_points']} points.")
            speak(f"You've earned {loyalty_points} loyalty points!")

            print("Thank you for your purchase!")
            speak("Thank you for your purchase!")

            # Ask if the user wants to continue or exit
            while True:
                cont = input("\nWould you like to make another purchase? (yes/no): ").strip().lower()
                if cont == 'yes':
                    break  # Allow the user to continue purchasing
                elif cont == 'no':
                    print("Thank you for using Kel's Vending. Have a great day!")
                    speak("Thank you for using Kel's Vending. Have a great day!")
                    exit()  # Exit the program
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")
                    speak("Invalid input. Please enter yes or no.")
            
            break  # Exit the payment loop and continue with the next iteration if 'yes' to purchase again

    except ValueError:
        print("Invalid input. Please enter a valid bill amount.")
        speak("Invalid input. Please enter a valid bill amount.")

# Inventory alert after each transaction
InventoryAlert()




 
