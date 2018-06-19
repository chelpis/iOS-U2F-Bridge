import json

class Task:
    dest = ""
    message = ""    

    def __init__(self, message):        
        self.message = message


class HIDTask(Task):    
    sw = ""

    def __init__(self, sw, message):        
        self.dest = "HID"         
        self.sw = sw
        self.message = message

class ChannelTask(Task):    
    funcName = ""
    args = []

    def __init__(self):        
        self.dest = "Channel" 
        # self.message = message

    def setFuncName(self, funcName):
        self.funcName = funcName
        self.setMessage()

    def setArgs(self, args):
        self.args = args
        self.setMessage()

    def setMessage(self):
        self.message = json.dumps({"funcName":self.funcName, "args":self.args})

class ChannelRawTask(Task):    
    def __init__(self, message):        
        self.dest = "Channel"                 
        self.message = message

# def main():
#     t = HIDTask("9000", "3345678")
#     print(t.dest)
#     # t.dest = "1"
#     print(t.message)

#     t1 = ChannelTask()
#     t1.setFuncName("func1")
#     t1.setArgs(["a1", "a2"])
#     print(t1.message)

# if __name__ == '__main__':
#     main()
