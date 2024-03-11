class exportableDict(dict):
    """Class for making dictionary .items()/.keys()/.items() exportable by casting their output to lists."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dictimplement_keys = self.keys
        self.__dictimplement_values = self.values
        self.keys = self.__exportable_keys
        """D.keys() -> a list object providing a view on D's keys"""
        self.values = self.__exportable_values
        """D.values() -> a list object providing a view on D's values"""
    def __exportable_keys(self) -> list:
        """D.__exportable_keys() -> a list object providing a view on D's keys"""
        return list(self.__dictimplement_keys())
    def __exportable_values(self) -> list:
        """D.__exportable_values() -> a list object providing a view on D's values"""
        return list(self.__dictimplement_values())
    def items(self) -> list:
        """D.items() -> a list object providing a view on D's items"""
        return list(zip(self.__dictimplement_keys(),self.__dictimplement_values()))