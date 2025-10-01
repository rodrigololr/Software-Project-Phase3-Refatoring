from cms.models import User, UserRole
from cms.views.logged_menu import LoggedMenu
from cms.views.menu import AbstractMenu, AppContext, MenuOptions, clear_screen
from cms.populate import populate


class Menu(AbstractMenu):
    def __init__(self):
        # acesso a instância singleton diretamente e popula o dados
        populate(AppContext())

    def show(self):
        try:
            self._main_menu()
        except KeyboardInterrupt:
            print("\nSaindo.")

    def _main_menu(self):
        while True:
            clear_screen()
            print("CMS\n")

            options: list[MenuOptions] = [
                {"message": "Fazer Login", "function": self.login},
                {
                    "message": "Registrar um novo usuário",
                    "function": self.create_user,
                },
            ]

            for i, option in enumerate(options):
                print(f"{i + 1}. {option['message']}")
            print("0. Sair")
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

    def create_user(self):
        first_name = input("Digite seu primeiro nome: ")
        last_name = input("Digite seu último nome: ")
        email = input("Digite seu email: ")
        username = input("Digite um username: ")
        password = input("Digite uma senha: ")

        user = User(first_name, last_name, email,
                    username, password, UserRole.USER)
        # acessa o repositório de usuários através do Singleton
        AppContext().user_repo.add_user(user)

        input("Usuário Criado! Clique Enter para voltar ao menu.")

    def login(self):
        while True:
            username = input("Username: ")
            password = input("Senha: ")

            try:
                # usa a instância Singleton para validar o usuário
                user = AppContext().user_repo.validate_user(username, password)
                # o construtor de LoggedMenu foi simplificado
                LoggedMenu(user).show()
                break
            except ValueError:
                clear_screen()
                print("Credenciais Inválidas!\n")
