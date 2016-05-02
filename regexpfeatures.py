# Author: Kaiwen Sun
### Regular Expressions Locating Valid Items Region of a Receipt ###
# featuring the start of items in a receipt
possible_start = [
        "Qty\s*Size\s*Item\s*Price",
        "---\s*ITEM\s*---\s*QTY\s*PRICE\s*MEMO\s*PLU",
        "QTY\s*ITEM\s*TOTAL",
        "Qty\s*Size\s*Item"
        ]

# featuring the end of items in a receipt
possible_end = [
        "Total",
        "a.+E.+a.+-.+\s{30,}.*a"
        ]

# featuring those receipts which are not a purchas and should not be counted
possible_ignore = [
        "MERCHANT COPY",
        "Paid Out Report",
        "Cash Drop Report",
        "Recall Order",
        "\*\*\*\* Waste \*\*\*\*",
        "Cash Drop Adjustment Report",
        "Subway Store",
        "\*\*\*DECLINED\*\*\*",
        "\*\*\*\* No Sale \*\*\*\*",
        "             SUBWAY Card",
        "\*    END-OF-DAY JOURNAL REPORTS    \*",
        "Bread Credits?",#Bread credits are used to register carriers that were damaged or expired. 
        "Productivity Report",
        "Cash Drop Report"
        ]

# featuring some special receipts that make no sense or that are printed while system crashe
possible_ignore_for_crash = [
        "Store #13398       tko \d\d/\d\d/\d\d \d\d:\d\d:\d\d",
        "Store #33607       tko \d\d/\d\d/\d\d \d\d:\d\d:\d\d",
        "Store #46480       tko \d\d/\d\d/\d\d \d\d:\d\d:\d\d",
        "Store #49417       tko \d\d/\d\d/\d\d \d\d:\d\d:\d\d", 
        "Store #40001       tko 08/31/15 14:59:40",
        "Reference No: 522620529965"
        ]

# combine features that should be ignored 
possible_ignore += possible_ignore_for_crash

### Regular Expressions Deciding Category of Items ###
# featuring sandwiches, such as Sub, SOTD(Sub of the day), flatbread, boxed lunch, and a few special pruned item names
possible_sandwich = [
        "^(?!.*with).*Sub(?!way)",
        "FlatB",         #flatbread sandwich
        "Flatbread",
        "SOTD FT",
        "SOTD 6in",       #Sub of the day
        "Ham FlatBd",
        "^(?!.*(add|EX)).*(Footlong|FtLong| FT |FtLng|(?!W)(?!Ex)Tr |fs | sr |fr )(?!.*(add|EX)).*$",
        "^(?!.*(add|EX)).*(6in|6\s?inch| 6s |6r |Br )(?!(add|EX)).*$",
        "6\"",
        "12\"",
        "BoxLn",     #boxed lunch, usually large quantity, can't ignore. no drink in BoxLn.
        "Spring Garden ChickenSld S",
        "RotisserieStyleChicken Su"
        ]

# featuring drinks, such as Fountain, Coffee, Bottled Warter. Soup is not viewed as drink.
possible_drink = [
        "Drink",
        "Drk",
        "DRK",
        "Ftn",
        "Fnt",
        "Bev",
        "Fount",
        "Coffee",
        "Bottle?",
        "Juice",
        "BtlWtr?",
        "BTL WATER",
        "Lemonade",
        "^(?!.*Soup).*\d+oz.*(?!.*Soup).*$"
        ]

# featuring items already known as neither sandwich nor drink
possible_otherkind = [
        #".", #this can be activated ONLY after making sure no sandwich or drink is ignored by mistake
        "0\.(\d[1-9]|[1-9]\d)",
        "Cookie",
        "Chips",
        "meal",
        "Add6in",
        "Milk",
        "Pizza",
        "Kids Toy",
        "AddFt",
        "Hot",
        "Item",
        "Dlx(FT|6)",
        "Salad",
        "Soup",
        "FVM",        #fresh value meal
        "Bag",
        "Salt",
        "Pepper",
        "NOBLE7\"",
        "Portn",
        "Extr6",
        "ExtrFT",
        "Apple",
        "Flatizza",     #Subway's version of pizza
        "RotisserieStyleChicken",
        "Icee",
        "Italian",
        "Fresh Toasted",
        "Spinach",         
        "Olives",
        "Onion",
        "Chipotle Southwest",
        "Creamy Sriracha",
        "Grated Parmesan Ch",
        "Mkt 205,138,133 - Tier",
        "Wrap",
        "AuntAn",
        "Discount",
        "\d{,2}% off",
        "EX ",
        "SMS",
        "UnKnown",
        "Employee",
        "SndPlt",
        "Platter",
        "Combo",
        "Pretzel",
        "American",
        "Tomato",
        "Cucumber",
        "Mayonnaise",
        "Mayo",
        "Provolone",
        "Toast",
        "Mustard",
        "Topping",
        "Pickle",
        "Lettuce",
        "Olive",
        "Brownie",
        "Muffin",
        "(add|Ext)",
        "Ranch",
        "Popcorn",
        "Ice Cream",
        "Side",
        "Pastry",
        "CAN - Fresh Value Mea",
        "Sausage & Egg BscMlt",
        "Bacon Egg & Cheese BscMlt",
        "Feast",
        "avocado",
        "Biscuit",
        "KIDS DISH",
        "Subway Cash Card",
        "KIDSTURK"
        ]

### Regular Expressions Used to Decide Sandwich's Size and Item's Quantity ###
# featuring 6-inch sandwich
possible_6insandwich = [
        "6\"",
        "6\s?[iI]n(ch)?",
        "^(?!.*(add|EX)).*(6[iI]n|6\s?[iI]nch| 6s |6r |Br )(?!(add|EX)).*$"   
        ]

# featuring 12-inch sandwich
possible_12insandwich = [
        "12\"",
        "12\s?in(ch)?",
        "^(?!.*(add|EX)).*(Footlong|FtLong| FT |FtLng|(?!Ex)Tr | dr |fs | sr |fr )(?!.*(add|EX)).*$"    
        ]

# featuring Mini (3-inch) sandwich
possible_minisandwich = [
        "3\"",
        "Mini"
        ]

# featuring possible quantity of items
possible_itemQty = [
        "\s[1-9]\d*\s(?!\s*oz)(?!\s*Inch)(?!\s*in)"
        ]
