import requests

class Rolimons():

    def __init__(self):
        catalog = requests.get("https://www.rolimons.com/itemapi/itemdetails")
        self.items = catalog.json()["items"]

    def getDemand(self, id: int):
        demandChart = {-1: "None", 0: 'terrible', 1: 'low', 2: 'normal', 3: 'high', 4: 'amazing'}
        if str(id) not in self.items:
            return -1
        
        itemDemand = self.items[str(id)][5]
        return demandChart[itemDemand], itemDemand

    def getValue(self, id: int):
        if str(id) not in self.items:
            return -1
        
        itemValue = self.items[str(id)][4]
        return itemValue
    
    def isProjected(self, id: int):
        if str(id) not in self.items:
            return -1
        
        isProj = (1 == self.items[str(id)][7])
        return isProj
    
    def toName(self, id: int):
        if str(id) not in self.items:
            return "None"

        name = self.items[str(id)][0]
        return name
    
    def displayStats(self, id: int):
        return f"Item: {self.toName(id)}\nProjected: {self.isProjected(id)}\nValue: {self.getValue(id)}\nDemand: {self.getDemand(id)}\n"
    
    def postTradeAd(self, cookies: str, items_giving: list, items_receiving: list, request_tags: str, player_id: int):
        url = "https://api.rolimons.com/tradeads/v1/createad"
        request_tags = request_tags.split(",")
        roli_cookies = {"_RoliVerification":cookies}
        data = {
            "player_id": player_id,
            "offer_item_ids": items_giving,
            "request_item_ids": items_receiving,
            "request_tags": request_tags
        }

        response = requests.post(url=url, cookies=roli_cookies, json=data)
        print(response)
        return response.json()


