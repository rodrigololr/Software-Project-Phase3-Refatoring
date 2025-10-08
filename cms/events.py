from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Observer(ABC):
    @abstractmethod
    def update(self, event_type: str, *args, **kwargs) -> None:
        # define como a interface do observador deve ser
        pass


#gerencia os eventos e notifica os observadores
class EventManager:
    # esse aqui no exemplo do guru lá é o publisher
    def __init__(self):
        self._subscribers: Dict[str, List[Observer]] = {}

    def subscribe(self, event_type: str, observer: Observer) -> None:
        # registra o observador para um tipo de evento específico
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(observer)

    def unsubscribe(self, event_type: str, observer: Observer) -> None:
        # remove o inscrito da lista de inscritos para um tipo de evento específico
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(observer)
            if not self._subscribers[event_type]:
                del self._subscribers[event_type]

    def notify(self, event_type: str, *args, **kwargs) -> None:
        # notifica todos os observadores inscritos sobre um evento específico
        if event_type in self._subscribers:
            for observer in list(self._subscribers[event_type]):
                try:
                    observer.update(event_type, *args, **kwargs)
                except Exception:
                    # Não deve interromper notificações a outros observadores.
                    # Se desejar, adicione logging aqui.
                    pass