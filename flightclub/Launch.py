# Class for Launch
 
class Launch:
 
    # Class Variable
    #animal = 'dog'
 
    # The init method or constructor
    def __init__(self, site, mission, vehicle):
 
        # Instance Variable
        self.site = site
        self.mission = mission
        self.vehicle = vehicle 
 

    # Add more instance variables
    # set launch angle 
    def setAngle(self, angle):
        self.angle = angle
    
    def setDist(self, distance):
        self.distance = distance
    

    # Retrieve instance variables
    def getAngle(self):
        return self.angle

    def getDist(self):
        return self.distance
 
 
# Driver Code
#Rodger = Dog("pug")
#Rodger.setColor("brown")
#print(Rodger.getColor())