#python CSV script practice
import csv
import argparse

#define cmd line args
parser = argparse.ArgumentParser(description = 'Generate Product Report & Team Report')
parser.add_argument('-t', '--team-file', help = 'teamMap file', required = True)
parser.add_argument('-p', '--product-file', help = 'productMaster file', required=True)
parser.add_argument('-s', '--sales-file', help = 'Sales file', required=True)

parser.add_argument('--team-report', help = 'Team Report file, OUTPUT', required=True)
parser.add_argument('--product-report', help = 'product sales report file, OUTPUT', required= True)
args = parser.parse_args()

#defining fieldNames for productMaster & Sales
sales_fieldNames = ['SaleID', 'ProductID', 'TeamID', 'Quantity', 'Discount'] 
product_fieldNames = ['ProductID', 'Name', 'Price', 'LotSize'] 

#list to hold data that I will use to make the relevant calculations
sales_data = []

#reading Sales.csv and processing it, essentially concatenating relevant data from the 3 files that I need to make the proper calculations
with open(args.sales_file, 'r', encoding='utf-8-sig') as csvSales:
    sales = csv.DictReader(csvSales, fieldnames=sales_fieldNames)
    for sale in sales:
        sale_data = {
            'SaleID': sale['SaleID'],
            'ProductID': sale['ProductID'],
            'TeamID': sale['TeamID'],
            'Quantity': sale['Quantity'],
            'Discount': sale['Discount']
        }
        #now add team Name to sale_data IF teamID matches in both sale and teamMap
        with open(args.team_file, 'r', encoding='utf-8-sig') as csvTeamMap:
            teamMap = csv.DictReader(csvTeamMap)
            for team in teamMap:
                if team['TeamID'] == sale['TeamID']:
                    sale_data['Team Name'] = team['Name']
                    break
        #now adding price and lotSize to sale_data IF productID matches in both sale and product
        with open(args.product_file, 'r', encoding='utf-8-sig') as csvProducts:
            productMast = csv.DictReader(csvProducts, fieldnames=product_fieldNames)
            for product in productMast:
                if product['ProductID'] == sale['ProductID']:
                    sale_data['Price'] = product['Price']
                    sale_data['Lot'] = product['LotSize']
                    break
        sales_data.append(sale_data)

# print(sales_data)

with open(args.team_file, 'r', encoding='utf-8-sig') as csvTeamMap:
    teamMap = csv.DictReader(csvTeamMap)
    team_dict = {}
    for team in teamMap:
        team_dict[team['TeamID']] = team['Name']

team_revenues = {}

for sale in sales_data:
    price = float(sale['Price'])
    quantity = int(sale['Quantity'])
    discount = float(sale['Discount'])
    lot = int(sale['Lot'])
    revenue = (price * quantity * lot)
    revnue = round(revenue, 2) #rounding bc $ 
    team_id = sale['TeamID']
    team_name = team_dict[team_id]
    if team_name in team_revenues:
        team_revenues[team_name] += revenue #rounding bc $
    else:
        team_revenues[team_name] = revenue #rounding bc $

# print(team_revenues) 

#-------------------------------------------------------------------------------------------------------
#now creating product-revnues, which will be used to make the ProductReport.csv output file
#-------------------------------------------------------------------------------------------------------

#create a dictionary of products: [Name, grossRevenue, totalUnits, and totalDiscount]
sales_data2 = []

#read Sales.csv and extract relevant data and place into sales_data2
with open(args.sales_file, 'r', encoding='utf-8-sig') as csvSales:
    sales = csv.DictReader(csvSales, fieldnames=sales_fieldNames)
    for sale in sales:
        sale_data2 = {
            'ProductID': sale['ProductID'],
            'Quantity': sale['Quantity'],
            'Discount': sale['Discount']
        }
        #now do the same with ProductMaster.csv 
        with open(args.product_file, 'r', encoding='utf-8-sig') as csvProducts:
            productMast = csv.DictReader(csvProducts, fieldnames=product_fieldNames)
            for product in productMast:
                if product['ProductID'] == sale['ProductID']:
                    sale_data2['Price'] = product['Price']
                    sale_data2['Lot'] = product['LotSize']
                    sale_data2['Name'] = product['Name']
                    break
        sales_data2.append(sale_data2)

#Now all the data requisite for the 'Product Report' calculation is in sales_data2

with open(args.product_file, 'r', encoding='utf-8-sig') as csvProductMaster:
    productMast2 = csv.DictReader(csvProductMaster, fieldnames=product_fieldNames)
    product_dict = {}
    for prod in productMast2:
        product_dict[prod['ProductID']] = prod['Name']

#dictionary to hold the product data necessary for calculating the requisite output
product_revenues = {}


#calculating grossRevenue, totalUnits, and DiscountCost and then placing in product_revnues along with Name
for sale in sales_data2:
    price = float(sale['Price'])
    quantity = int(sale['Quantity'])
    discount = float(sale['Discount'])
    lot = int(sale['Lot'])
    revenue = (price * quantity * lot)
    total_units = (quantity * lot)
    # discount_cost = (revenue-(((100 - discount)/100)*revenue)) #old, roundabout discount calculation
    discount_cost = ((discount/100) * revenue)
    revenue = round(revenue, 2) #rounding bc $ 
    productID = sale['ProductID']
    product_name = product_dict[productID]
    if product_name in product_revenues:
        product_revenues[product_name]['GrossRevenue'] += revenue 
        product_revenues[product_name]['TotalUnits'] += total_units
        product_revenues[product_name]['DiscountCost'] += discount_cost
    else:
        product_revenues[product_name] = {
            'Name' : product_name,
            'GrossRevenue' : round(revenue, 2), #rounding bc $ (redundant)
            'TotalUnits' : total_units,
            'DiscountCost' : discount_cost
        }

# print(product_revenues) 

# Write team report to CSV file, sorted in descending order by grossRevenue
with open(args.team_report, 'w', newline='', encoding='utf-8-sig') as csvTeamReport:
    fieldnames = ['Team', 'GrossRevenue']
    writer = csv.DictWriter(csvTeamReport, fieldnames=fieldnames)
    writer.writeheader()
    team_revenues_sorted = dict(sorted(team_revenues.items(), key=lambda item: item[1], reverse=True))
    for team, revenue in team_revenues_sorted.items():
        writer.writerow({'Team': team, 'GrossRevenue': revenue})

# Write product report to CSV file, sorted in descending order by grossRevenue
with open(args.product_report, 'w', newline='', encoding='utf-8-sig') as csvProductReport:
    fieldnames = ['Name', 'GrossRevenue', 'TotalUnits', 'DiscountCost']
    writer = csv.DictWriter(csvProductReport, fieldnames=fieldnames)
    writer.writeheader()
    product_revenues_sorted = sorted(product_revenues.values(), key=lambda x: x['GrossRevenue'], reverse=True)
    for product in product_revenues_sorted:
        writer.writerow({'Name': product['Name'], 'GrossRevenue': product['GrossRevenue'], 'TotalUnits': product['TotalUnits'], 'DiscountCost': product['DiscountCost']})





