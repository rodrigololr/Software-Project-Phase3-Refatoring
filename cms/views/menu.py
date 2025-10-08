from abc import ABC, abstractmethod
import os
import threading
from typing import Callable, TypeVar, TypedDict

from cms.repository import (
    AnalyticsRepository,
    CommentRepository,
    MediaRepository,
    PermissionRepository,
    PostRepository,
    SiteRepository,
    UserRepository,
)
from cms.services.languages import LanguageService

MenuOptions = TypedDict(
    "MenuOptions", {"message": str, "function": Callable[..., None]}
)

M = TypeVar("M")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


class AbstractMenu(ABC):
    @abstractmethod
    def show(self):
        pass

    @staticmethod
    def prompt_menu_option(
        options: list[MenuOptions],
        display_title: Callable[..., None],
        cancel_option: str = "Voltar",
    ):
        while True:
            clear_screen()
            display_title()

            for i, option in enumerate(options):
                print(f"{i + 1}. {option['message']}")
            print(f"0. {cancel_option}")
            print(" ")

            try:
                selected_option = int(
                    input("Digite o número da opção para selecioná-la: ")
                )
            except ValueError:
                print("Opção inválida.\n")
                continue

            if selected_option == 0:
                break

            if selected_option < 0 or selected_option > len(options):
                print("Opção inválida.\n")
                continue

            clear_screen()
            options[selected_option - 1]["function"]()

    @staticmethod
    def prompt_generic(
        items: list[M],
        title: str,
        callback: Callable[[M], None],
        option_text: Callable[[M], str],
    ):
        while True:
            clear_screen()

            print(title)
            for i, item in enumerate(items):
                print(f"{i + 1}. {option_text(item)}")

            print("0. Voltar")
            print(" ")

            try:
                selected_option = int(
                    input("Digite o número do site para selecioná-lo: ")
                )
            except ValueError:
                print("Opção inválida.\n")
                continue

            if selected_option == 0:
                return

            if selected_option < 0 or selected_option > len(items):
                print("Opção inválida.\n")
                continue

            selected_item = items[selected_option - 1]
            callback(selected_item)


# aplicar o sigleton aqui, parece encaixar bem
class AppContext:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # double-checked locking
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    inst = super(AppContext, cls).__new__(cls)
                    inst.__site_repo = SiteRepository()
                    inst.__post_repo = PostRepository()
                    inst.__user_repo = UserRepository()
                    inst.__comment_repo = CommentRepository()
                    inst.__media_repo = MediaRepository()
                    inst.__analytics_repo = AnalyticsRepository()
                    inst.__permission_repo = PermissionRepository()
                    inst.__lang_service = LanguageService()
                    cls._instance = inst
        return cls._instance

    @property
    def site_repo(self) -> SiteRepository:
        return self.__site_repo

    @property
    def post_repo(self) -> PostRepository:
        return self.__post_repo

    @property
    def user_repo(self) -> UserRepository:
        return self.__user_repo

    @property
    def comment_repo(self) -> CommentRepository:
        return self.__comment_repo

    @property
    def media_repo(self) -> MediaRepository:
        return self.__media_repo

    @property
    def analytics_repo(self) -> AnalyticsRepository:
        return self.__analytics_repo

    @property
    def permission_repo(self) -> PermissionRepository:
        return self.__permission_repo

    @property
    def lang_service(self) -> LanguageService:
        return self.__lang_service

    def reset_context(self):
        self.__site_repo = SiteRepository()
        self.__post_repo = PostRepository()
        self.__user_repo = UserRepository()
        self.__media_repo = MediaRepository()
        self.__comment_repo = CommentRepository()
        self.__analytics_repo = AnalyticsRepository()
        self.__permission_repo = PermissionRepository()
        self.__lang_service = LanguageService()
