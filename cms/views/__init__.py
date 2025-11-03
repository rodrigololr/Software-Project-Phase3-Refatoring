from cms.models import User, UserRole
from cms.views.logged_menu import LoggedMenu
from cms.views.menu import AbstractMenu, MenuOptions, clear_screen
from cms.context import AppContext
from cms.populate import populate
from cms.exceptions import ValidationError, AuthenticationError, RepositoryError, InvalidNameError
from cms.utils import validate_name, validate_email, validate_username, validate_password


class Menu(AbstractMenu):
    def __init__(self):
        # acesso a instância singleton diretamente e popula o dados
        try:
            populate(AppContext())
        except Exception as e:
            print(f"Erro ao popula dados: {str(e)}")
            raise

    def show(self):
        try:
            self._main_menu()
        except KeyboardInterrupt:
            print("\n Saindo.")
        except Exception as e:
            print(f"Erro inesperado: {str(e)}")

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
                input("Clique Enter para continuar.")
                continue

            if selected_option == 0:
                break

            if selected_option < 0 or selected_option > len(options):
                print("Opção inválida.\n")
                input("Clique Enter para continuar.")
                continue

            clear_screen()
            try:
                options[selected_option - 1]["function"]()
            except Exception as e:
                print(f"Erro ao executar opção: {str(e)}")
                input("Clique Enter para voltar.")

    def create_user(self):
        try:
            first_name = validate_name(input("Digite seu primeiro nome: "), "Primeiro nome")
            last_name = validate_name(input("Digite seu último nome: "), "Último nome")
            email = validate_email(input("Digite seu email: "))
            username = validate_username(input("Digite um username: "))
            password = validate_password(input("Digite uma senha: "))

            user = User(first_name, last_name, email,
                        username, password, UserRole.USER)
            # acessa o repositório de usuários através do Singleton
            AppContext().user_repo.add_user(user)

            print("Usuário criado com sucesso!")
            input("Clique Enter para voltar ao menu.")
            
        except InvalidNameError as e:
            print(f"Nome inválido: {e}")
            input("Clique Enter para voltar.")
        except ValidationError as e:
            print(f"Erro de validação: {e}")
            input("Clique Enter para voltar.")
        except Exception as e:
            print(f"Erro ao criar usuário: {str(e)}")
            input("Clique Enter para voltar.")

    def login(self):
        while True:
            try:
                username = input("Username: ").strip()
                if not username:
                    raise ValidationError("Username não pode estar vazio.")
                
                password = input("Senha: ").strip()
                if not password:
                    raise ValidationError("Senha não pode estar vazia.")

                # usa a instância Singleton para validar o usuário
                user = AppContext().user_repo.validate_user(username, password)
                # o construtor de LoggedMenu foi simplificado
                LoggedMenu(user).show()
                break
                
            except AuthenticationError:
                clear_screen()
                print("Credenciais inválidas!\n")
                input("Clique Enter para tentar novamente.")
            except ValidationError as e:
                clear_screen()
                print(f"Erro: {e}\n")
                input("Clique Enter para tentar novamente.")
            except RepositoryError as e:
                clear_screen()
                print(f"Erro no sistema: {e}\n")
                input("Clique Enter para tentar novamente.")
            except Exception as e:
                clear_screen()
                print(f"Erro inesperado: {str(e)}\n")
                input("Clique Enter para tentar novamente.")
