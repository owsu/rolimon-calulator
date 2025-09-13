from rolimons import Rolimons
import math

# Simple Rolimons Trade Calculator
rolimons = Rolimons()

yourSideValue = 0
theirSideValue = 0

yourHighestDemand = 0
theirHighestDemand = 0

print("Items you are giving: (splice int with commas)")
itemsGiving = input("")
itemsGiving = itemsGiving.split(",")
for id in itemsGiving:
    id = int(id)
    demandName, demandId = rolimons.getDemand(id)
    if demandId > yourHighestDemand:
        yourHighestDemand = demandId

print("Items you are receiving: (splice int with commas)")
itemsReceiving = input("")
itemsReceiving = itemsReceiving.split(",")
for id in itemsGiving:
    id = int(id)
    demandName, demandId = rolimons.getDemand(id)
    if demandId > theirHighestDemand:
        theirHighestDemand = demandId

for id in itemsGiving:
    yourSideValue += rolimons.getValue(id)

for id in itemsReceiving:
    theirSideValue += rolimons.getValue(id)

isUpgrading = (len(itemsGiving) > len(itemsReceiving)) # upgrading is the act of giving multiple small items for a bigger item

for id in itemsGiving:
    print(rolimons.displayStats(id))
    print("----------------------")
print(yourSideValue)
print("==========FOR==========")

for id in itemsReceiving:
    print(rolimons.displayStats(id))
    print("----------------------")
print(theirSideValue)

if isUpgrading: # if we are upgrading then losing up to 5% is fine
    print("You are upgrading")
    calculatedRate = 5 / (1 + (theirHighestDemand/100))
    
    if (yourSideValue/theirSideValue <= calculatedRate):
        print("Adequate trade")
    else:
        print("You are overpaying too much")
else: # if we are downgrading then we need a gain that slightly decreases the more expensive the item is, but increases based off demand
    print("You are downgrading")
    calculatedRate = (1/ (2*math.log(yourSideValue, 10))) * (1+ (yourHighestDemand/100))

    if (yourSideValue/theirSideValue >= calculatedRate):
        print("Adequate trade")
    else:
        print("You are getting lowballed")
     


