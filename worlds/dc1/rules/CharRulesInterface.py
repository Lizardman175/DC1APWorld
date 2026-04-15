import abc
from BaseClasses import CollectionState

# Might be able to remove as everything else currently inherits from CharRules.py, but future changes might bring this back
class CharRulesInterface(abc.ABC):

    @abc.abstractmethod
    def xiao_available(self, state: CollectionState, player: int) -> bool:
        pass

    @abc.abstractmethod
    def goro_available_only(self, state: CollectionState, player: int) -> bool:
        pass

    @abc.abstractmethod
    def goro_available(self, state: CollectionState, player: int) -> bool:
        pass

    @abc.abstractmethod
    def ruby_available_only(self, state: CollectionState, player: int) -> bool:
        pass

    @abc.abstractmethod
    def ruby_available(self, state: CollectionState, player: int) -> bool:
        pass

    @abc.abstractmethod
    def ungaga_available_only(self, state: CollectionState, player: int) -> bool:
        pass

    @abc.abstractmethod
    def ungaga_available(self, state: CollectionState, player: int) -> bool:
        pass

    @abc.abstractmethod
    def osmond_available_only(self, state: CollectionState, player: int) -> bool:
        pass

    @abc.abstractmethod
    def osmond_available(self, state: CollectionState, player: int) -> bool:
        pass

    # Not actually a character, but functions in a similar way
    @abc.abstractmethod
    def got_accessible(self, state: CollectionState, player: int) -> bool:
        pass