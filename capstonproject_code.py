import pandas as pd

#upload CSV file
file_path = 'C:\capstoneproject\groceries_stock.csv'

# Read the CSV file
df = pd.read_csv(file_path)

# Display the first few rows of the DataFrame
print(df.head())

# To check the data types
df.info()

# Renaming the columns, because it would be easier to understand what that means.
df.columns = ['itemID', 'itemName', 'itemGroup','stock', 'price']
df.head()

# Checking for the missing values
nan_values = df.isna().sum()
nan_values

# there are missing values
df = df.dropna(subset=['itemID','itemName', 'stock', 'price'])

df['stock'] = df['stock'].astype('int')
df['price'] = df['price'].astype('int')
df.info()  # They are in correct datatype now

# Counting the itemName based on itemGroup
item_counts = df.groupby('itemGroup')['itemName'].count()

# Displaying the counts
print(item_counts)

def display_products(df):
    print("\nList of Saleable Products:")
    print(df)

def select_item_counts(df):
    item_group = input("Enter the item group: ").lower() 
    df['itemGroup'] = df['itemGroup'].str.lower()
    sku_counts = df[df['itemGroup'] == item_group].groupby('itemGroup').size().reset_index(name='count')
    
    if not sku_counts.empty:
        item_names = df[df['itemGroup'] == item_group]['itemName'].unique()
        print(f"Item names for item group '{item_group}': {', '.join(item_names)}")
    else:
        print(f"No SKUs found for item group '{item_group}'")
        return pd.DataFrame()  # Return an empty DataFrame if no SKUs are found
    
    return df[df['itemGroup'] == item_group]

def process_item_selection(df, cart):
    selected_group = select_item_counts(df)

    if not selected_group.empty:
        # Sorting the filtered DataFrame by itemGroup in descending order
        selected_group_sorted = selected_group.sort_values(by='itemGroup', ascending=False)
        print(selected_group_sorted)
        
        # Allow the user to select an item name
        item_name = input("Enter the item name: ").lower()
        selected_item = selected_group_sorted[selected_group_sorted['itemName'].str.lower() == item_name]
        
        if not selected_item.empty:
            stock = selected_item['stock'].sum()  # Assuming 'stock' is the column name for stock quantities
            price = float(selected_item['price'].values[0])  # Assuming 'price' is the column name for item prices
            # Allow the user to input a quantity
            user_quantity = int(input("Enter the quantity: "))

            if user_quantity <= stock:
                print("Your item is successfully added to cart")
                cart.append({'itemName': item_name, 'quantity': user_quantity, 'totalPrice': user_quantity * price})
            else:
                print("We are out of stock. Cannot proceed.")
        else:
            print(f"No data found for item name '{item_name}'")
    else:
        print("No data available for the selected item group.")

def process_payment(total_amount):
    print("Select payment method:")
    print("1. Cashless")
    print("2. Cash")
    payment_method = input("Enter the number of your payment method: ")

    if payment_method == "1":
        confirmation = input("Are you sure to proceed the payment? (Yes/Cancelled): ")
        if confirmation.lower() == "yes":
            print("Transaction successful!")
            return True
        elif confirmation.lower() == "cancelled":
            print("Transaction cancelled.")
            return False
        else:
            print("Invalid input. Transaction cancelled.")
            return False
    
    elif payment_method == "2":
        try:
            cash = float(input("Enter the amount of cash: "))
            if cash < total_amount:
                print("Transaction failed. Insufficient cash.")
                return False
            elif cash == total_amount:
                print("Transaction successful!")
                return True
            else:
                change = cash - total_amount
                print(f"Transaction successful! Your change is {change:.2f}")
                return True
        except ValueError:
            print("Invalid amount entered. Please enter a valid number.")
            return False
        
    else:
        print("Invalid payment method selected.")
        return False

def update_stock(df, cart):
    for item in cart:
        item_name = item['itemName']
        quantity_purchased = item['quantity']
        df.loc[df['itemName'] == item_name, 'stock'] -= quantity_purchased
    print("Stock updated successfully.")

#Create the main features for user to shopping
def main(df):
    cart = []
    while True:
        print("\nMenu:")
        print("1. View Products")
        print("2. Make an Order")
        print("3. Exit")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            display_products(df)
        elif choice == '2':
            process_item_selection(df, cart)
            add_more = input("Do you want to add more products? (yes/no): ").lower()
            if add_more != 'yes':
                if cart:
                    print("\n----- Bill -----")
                    print(f"{'Item':<15}{'Quantity':<10}{'Total Price':<10}")
                    print("-" * 35)
                    for item in cart:
                        print(f"{item['itemName'].capitalize():<15}{item['quantity']:<10}{float(item['totalPrice']):<10.2f}")
                    total_amount = sum(float(item['totalPrice']) for item in cart)
                    print("-" * 35)
                    print(f"{'Total Amount':<25}{total_amount:.2f}")

                    if process_payment(total_amount):
                        update_stock(df, cart)
                        print("\nUpdated stock:")
                        print(df)
                        break  # Stop the program after updating the stock
        elif choice == '3':
            print("Thank you for shopping!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main(df)

# Initialize an empty DataFrame to store membership data
membership_df = pd.DataFrame(columns=['Name', 'Phone Number'])

def ask_membership():
    response = input("Do you want to create a membership? (yes/no): ").strip().lower()
    if response == 'yes':
        name = input("Please enter your name: ").strip()
        phone_number = input("Please enter your phone number: ").strip()
        # Add the new member to the DataFrame using pd.concat
        global membership_df
        new_member = pd.DataFrame({'Name': [name], 'Phone Number': [phone_number]})
        membership_df = pd.concat([membership_df, new_member], ignore_index=True)
        print("Thank you for becoming a member!")
    else:
        print("Thank you for shopping with us!")

# Example usage after a transaction
ask_membership()

# Display the membership DataFrame
membership_df.columns = ['Name', 'Phone Number']
membership_df.head()