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

def main(df):
    cart = []
    while True:
        process_item_selection(df, cart)
        
        # Ask for user to add more product
        add_more = input("Do you want to add more products? (yes/no): ").lower()
        if add_more != 'yes':
            print("Okay, stopping.")
            break
    
    if cart:
        print("\n----- Bill -----")
        print(f"{'Item':<15}{'Quantity':<10}{'Total Price':<10}")
        print("-" * 35)
        for item in cart:
            print(f"{item['itemName'].capitalize():<15}{item['quantity']:<10}{float(item['totalPrice']):<10.2f}")
        total_amount = sum(float(item['totalPrice']) for item in cart)
        print("-" * 35)
        print(f"{'Total Amount':<25}{total_amount:.2f}")

        # Call process_payment with total_amount
        if process_payment(total_amount):
            update_stock(df, cart)
            print("\nUpdated stock:")
            print(df)  # Print the DataFrame to see the updated stock

# Select payment method
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
    
    else:
        print("Invalid payment method selected.")
        return False

def update_stock(df, cart):
    for item in cart:
        item_name = item['itemName']
        quantity_purchased = item['quantity']
        df.loc[df['itemName'] == item_name, 'stock'] -= quantity_purchased
    print("Stock updated successfully.")

main(df)