import threading

from openai_cost_logger import OpenAICostLogger, DEFAULT_LOG_PATH

""" Metaclass for creating singletons."""
class Singleton(type):
    _instances = {}
    # we are going to redefine (override) what it means to "call" a class
    # as in ....  x = MyClass(1,2,3)
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # we have not every built an instance before.  Build one now.
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        else:
            instance = cls._instances[cls]
            # here we are going to call the __init__ and maybe reinitialize.
            if hasattr(cls, '__allow_reinitialization') and cls.__allow_reinitialization:
                # if the class allows reinitialization, then do it
                instance.__init__(*args, **kwargs)  # call the init again
        return instance
    
"""Singleton class for the OpenAICostLogger class."""
class OpenAICostLogger_Singleton(metaclass=Singleton):
    def __init__(self, experiment_name: str, cost_upperbound: float, log_folder: str = DEFAULT_LOG_PATH):
        """Initializes the OpenAICostLogger_Singleton class.

        Args:
            experiment_name (_type_): the name of the experiment.
            log_folder (_type_): the folder where the logs will be stored.
            cost_upperbound (_type_): the upperbound of the cost.
        """
        self.__allow_reinitialization = False # prevent reinitialization of the singleton.
        self.__cost_logger = OpenAICostLogger(
            experiment_name=experiment_name,
            cost_upperbound=cost_upperbound,
            log_folder=log_folder
        ) 
        self.lock = threading.Lock() # Lock to ensure thread safety when updating the cost logger.
        
    
    def update_cost(self, response: dict, input_cost: float, output_cost: float = 0):
        with self.lock:
            self.__cost_logger.update_cost(
                response=response,
                input_cost=input_cost,
                output_cost=output_cost
            )