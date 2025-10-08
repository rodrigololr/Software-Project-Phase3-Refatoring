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


