from abc import ABC, abstractmethod
from cms.models import User, Post


class NotificationAdapter(ABC):
    """Interface para adaptadores de notificação."""

    @abstractmethod
    def notify(self, user: User, message: str) -> None:
        pass


class ConsoleNotificationAdapter(NotificationAdapter):
    """Adapter que envia notificações via console (stdout)."""

    def notify(self, user: User, message: str) -> None:
        print(f"\n📢 Notificação para {user.first_name}:")
        print(f"   {message}\n")


class EmailNotificationAdapter(NotificationAdapter):
    """Adapter que simula envio de e-mail (em produção, integra com SMTP)."""

    def notify(self, user: User, message: str) -> None:
        print(f"📧 E-mail enviado para {user.email}: {message}")


class LogNotificationAdapter(NotificationAdapter):
    """Adapter que registra notificações em log."""

    def __init__(self):
        self.__logs = []

    def notify(self, user: User, message: str) -> None:
        log_entry = f"[LOG] {user.username}: {message}"
        self.__logs.append(log_entry)
        print(log_entry)

    def get_logs(self) -> list[str]:
        return self.__logs
