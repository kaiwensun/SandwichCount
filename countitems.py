# Author: Kaiwen Sun
import json
import re
import sys
from pyspark import SparkContext  #not necessary in Jupyter
from regexpfeatures import *     #regular expression features

#RegExp to locate region of saled items in a receipt
re_startItems = re.compile("|".join(possible_start))
re_endItems = re.compile("|".join(possible_end),re.IGNORECASE)
re_ignore = re.compile("|".join(possible_ignore),re.IGNORECASE)
    
#RegExp to categorize saled items (sandwiches, drinks, others)
re_sandwich = re.compile("|".join(possible_sandwich),re.IGNORECASE)
re_drink = re.compile("|".join(possible_drink),re.IGNORECASE)
re_otherkind = re.compile("|".join(possible_otherkind),re.IGNORECASE)

#RegExp to decide sandwich size and item quantity
re_6insandwich = re.compile("|".join(possible_6insandwich))
re_12insandwich = re.compile("|".join(possible_12insandwich))
re_minisandwich = re.compile("|".join(possible_minisandwich))
re_itemQty = re.compile("|".join(possible_itemQty))

def warning(msg):
    """
    print warning message. currently print message to stderr. may also changed to write to log file.
    @param msg: warning message to be printed
    """
    sys.stderr.write("WARNING: "+msg+"\r\n")

def isItem(line):
    """
    Decide whether a line of string is an item. Invoked by locateItems. A 
    line of item is assumed not empty, with less than 7 '-' or '_', not
    free of charge
    @param line: a line of string
    @return True if is an item, False if is not an item.
    """
    re_notItem = re.compile(r"^\s*$|((-|_|\*).*){7,}|0\.00|^(?!.*[b-zA-DF-Z]+).*$")
    if not re_notItem.search(line):
        return True
    else:
        return False

def sandwichSize(line):
    """
    Decide sandwich size in inch. There are three kinds of sandwich size:
        Foot-long 12 inches
        Half-long 6 inches
        Mini 3 inches (rare)
    If fail to decide, by default assume the sandwich is 12 inches.
    @param line: a line of sandwich item from a receipt
    @return size of sandwich (3,6 or 12)
    """
    if re_6insandwich.search(line):
        return 6
    if re_12insandwich.search(line):
        return 12
    if re_minisandwich.search(line):
        return 3
    #warning("++++++++++++++++++++\r\nsandwichSize() can't decide size. set 12 by default\r\n"+line)
    return 12

def itemQty(line,sz):
    """
    Decide an item's quantity. Quantity can be any integer surrounded by whitespace.
    If there is one such integer, return it as quantity;
    if there are multiple such integers, use guessQty() to predict a reasonable quantity;
    if there is no such integer, use guessQty() to predict a reasonable quantity.
    """
    result = re_itemQty.findall(line)
    if len(result)==1:
        return int(result[0])
    if len(result)>1:
        #warning("+++++++++++++++++++\r\nitemQty() find multiple integers in the line. use 1st by default\r\n"+line)
        return guessQty(line,result,sz)
    if len(result)==0:
        #warning("+++++++++++++++++++\r\nitemQty() find no integer in the line. use 1 by default\r\n"+line)
        return guessQty(line,range(1,10),sz)
    
def line2count(line):
    """
    convert a line to a 3-tuple count of (sandwich_count, drink_count, sandwich_in_inches)
    @param line: a line of item
    @return a 3-tuple (sandwich_count, drink_count, sandwich_in_inches)
    """
    if re_drink.search(line):
        cnt = itemQty(line,-1)
        return (0,cnt,0)
    elif re_sandwich.search(line):
        sz = sandwichSize(line)
        cnt = itemQty(line,sz)
        return (cnt,0,cnt*sz)
    elif re_otherkind.search(line):
        return (0,0,0)
    else:
        msg = "Unknown item: "+line
        warning(msg)
        return (0,0,0)

def guessQty(line,qtylst,sz):
    """
    Guess the quantity of ambiguous item. The guess is based the category 
    of item, the total price of the item, and a reasonable range of unit 
    price of this category of item. This function chooses one from the possible
    quantity from qtylst such that the unit price of the item is reasonable.
    @param line: a line of item
    @param qtylst: a list of possilble quantity (string) of the item
    @param sz: size of sandwich (3, 6 or 12) drink (viewed as sz=-1)
    @return guessed quantity of item
    """
    #get price
    price_lst = re.findall("\d+\.\d\d(?!\d)",line)
    qtylst = map(lambda qty:int(qty),qtylst)
    if len(price_lst)==0:
        return min(qtylst)
    price = float(price_lst[0])
    if sz==12:    #12inches sandwich
        if price<1.5:
            return 0
        lst = filter(lambda unit_price:True if (unit_price[0]>=4 and unit_price[0] <9) else False,map(lambda q:(price/q,q),qtylst))
        return qtylst[0] if len(lst)==0 else lst[0][1]
    if sz==6:    #6inch sandwich
        lst = filter(lambda unit_price:True if (unit_price[0]>=2 and unit_price[0] <5) else False,map(lambda q:(price/q,q),qtylst))
        return qtylst[0] if len(lst)==0 else lst[0][1]
    if sz==3:    #mini sandwich
        lst = filter(lambda unit_price:True if (unit_price[0]>=1.5 and unit_price[0] <=3) else False,map(lambda q:(price/q,q),qtylst))
        return qtylst[0] if len(lst)==0 else lst[0][1]
    if sz==-1:    #drink
        lst = filter(lambda unit_price:True if (unit_price[0]>=1 and unit_price[0] <=5) else False,map(lambda q:(price/q,q),qtylst))
        return qtylst[0] if len(lst)==0 else lst[0][1]
    return qtylst[0]
    
def locateItems(receipt):
    """
    This function takes in one single receipt, find those lines of item in the receipt string.
    The assumed defination of 'lines of item' is any line satisfying all of the following conditions:
    (1)after the line containing
        'Qty Size Item Price' or 
        '--- ITEM --- QTY PRICE MEMO PLU' or
        'QTY ITEM TOTAL'
    (2)before the line containing 'Total'
    (3)judged as an item by function isItem()
    (4)the receipt has no line fitting the RegExp re_ignore
    If starting line or ending line is not found, and if the receipt 
    is not ignored by re_ignore, call warning().
    Some information is acquired from http://www.sametch.com/images/SubwayPOS_User_Manual.pdf
    @param receipt: a pair (int:receipt_index, string:receipt_content)
    @return: a list of lines consisting sold items
    """
    str_receipt = receipt[1]
    start = False
    end = False
    ignore = False

    lines = re.split("\r\n|\n",str_receipt)
    items = []
    for line in lines:
        if start==False:
            if re_startItems.search(line):
                start = True    #start of item list
            elif re_ignore.search(line):
                ignore = True
        else:
            if re_endItems.search(line):
                end = True
                break    #end of item list
            elif isItem(line):
                items.append(line)
    if (start==False or end==False) and not ignore:
        msg = "\r\n/=====================================================\\\r\n"
        msg += "The receipt "+str(receipt[0])+" is not in expected format (start="+str(start)+", end="+str(end)+", ignore="+str(ignore)+")\r\n"
        msg += receipt[1]
        msg += "\r\n\\======================================================/\r\n"
        warning(msg)
    return (receipt[0],items)

def receiptLines2count(lst_of_line):
    """
    convert lines in one receipt to the count of sandwich, drink and sandwich length in inches.
    @param lst_of_line: a python list of lines in one receipt
    @return a list of 3-tuples (cnt_sandwich, cnt_drink, len_sandwich)
    """
    return map(lambda line:line2count(line),lst_of_line)

def main():
    """
    Count Subway sandwich and drink sales from receipt file.
    """
    # Create spark context object. Not necessary in Jupyter. Necessary in plain python environment.
    sc = SparkContext()

    # Read lines from json file
    filename = "sample-receipts.json"
    rdd = sc.textFile(filename)

    # Convert lines of file to a list of (index, receipt_content) pairs
    jsontxt = rdd.map(json.loads).zipWithIndex().map(lambda (k,v):(v,k['receipt']))

    # Locate items in receipts and collect all lines of item
    all_items = jsontxt.map(locateItems).cache()

    # Convert each item to a 3-tuple (sandwich_count, drink_count, sandwich_size)
    lst_of_tuples = all_items.flatMap(lambda onereceipt:receiptLines2count(onereceipt[1]))

    # Sum up all 3-tuples to get total counts
    final_result = list(lst_of_tuples.reduce(lambda t1,t2:(t1[0]+t2[0],t1[1]+t2[1],t1[2]+t2[2])))
    final_result[2]=final_result[2]/float(12)
    final_result = tuple(final_result)
    
    #print result to stdout
    print "There are %d sandwiches, %d drinks. The total length of sandwiches are %.2f feet" % final_result

#Program entrance
main()


