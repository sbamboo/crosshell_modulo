import pickle

class serializationWrapper():
    def __init__(self):
        pass
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

    def customimplementation_return(self,obj,buffer_write_method):
        """
        Function that takes in an object and returns crsh-raw-pipedata, and sends it to crosshells output buffer, to be pickedup by the pipeline.
        """
        buffer_write_method( self.makePipeRaw(obj) )


class ArgumentManager():
    """
    Class for handling arguments, it takes arguments then the class it self and its attributes works as an object usable from inside the cmdlet scope.
    The class does ingest/load the data and perform some operations for example deserializing data:
    %piperaw%<hex-of-pickel>%piperaw%   =>   <object>
    """
    def __init__(self,arguments=list,serializationWrapper=object,buffer_write_method=None,stringJoiner=" "):
        self.__buffer_write_method = buffer_write_method
        self.__serializationWrapper = serializationWrapper
        self.__stringJoiner = stringJoiner
        self.oargv = arguments
        self.soargv = stringJoiner.join(arguments)
        self.argv = self.__deserialize_piperaw(arguments)
        self.sargv = stringJoiner.join(self.argv)

    def __call__(self):
        """Calling the argument manager will return the `argv` method."""
        return self.argv
    def __str__(self):
        return str(self.argv)

    def __deserialize_piperaw(self,data):
        """Method to deserilia."""
        new = []
        for part in data:
            if self.__serializationWrapper.isPipeRaw(part) == True:
                new.append( self.__serializationWrapper.getObj(part) )
            else:
                new.append( part )
        return new

    def _asignSerilizationWrapper(self,serializationWrapper=object):
        '''Method to asign a serilizationWrapper instance.'''
        self.__serializationWrapper = serializationWrapper

    def _asignBufferWriteMethod(self,buffer_write_method):
        '''Method to asign a buffer-write method.'''
        self.__buffer_write_method = buffer_write_method

    def returnObjToBuffer(self,*objects):
        """
        Function that takes any number of objects and seriliazes them to text before outputing them to crosshells buffer, to be picked up by the pipeline.
        """
        for obj in objects:
            des = self.__serializationWrapper.makePipeRaw(obj)
            if self.__buffer_write_method == None:
                print(des)
            else:
                self.buffer_write_method(des)

t = ArgumentManager(["hello"],serializationWrapper=serializationWrapper(),buffer_write_method=print)

print(t)