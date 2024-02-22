import pickle
      
class serializationWrapper():
    def __init__(self,buffer_bwrite,buffer_cwrite):
        self.instruct_bwrite = buffer_bwrite
        self.instruct_cwrite = buffer_cwrite

    def serialize(self,obj):
        '''Function to serialize an object to text.'''
        return 'pickle', pickle.dumps(obj).hex()
    
    def deserialize(self,data):
        '''Function to deserialize an object from text.'''
        return pickle.loads(bytes.fromhex(data))
    
    def makePipeRaw(self,obj):
        '''Function to serialize an object to text adding the %piperaw% tags.'''
        return "%piperaw%"+self.serialize(obj)+"%piperaw%"

    def isPipeRaw(self,possiblePipeRaw):
        '''Checks if an inputted text has the %piperaw% tags.'''
        if possiblePipeRaw.strip("").startswith("%piperaw%") and possiblePipeRaw.strip("").endswith("%piperaw%"):
            return True
        else:
            return False
    
    def getObj(self,possiblePipeRaw):
        '''If inputed text has %piperaw% tags return deserialized object.'''
        if self.isPipeRaw(possiblePipeRaw):
            return self.deserialize(possiblePipeRaw)
        else:
            return None

    def customimplementation_return(self,obj):
        """
        Function that takes in an object and returns crsh-raw-pipedata, and sends it to crosshells output buffer, to be pickedup by the pipeline.
        """
        self.instruct_bwrite( self.makePipeRaw(obj) )