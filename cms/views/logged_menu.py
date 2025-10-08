import os
from cms.models import User, UserRole
from cms.views.menu import AbstractMenu

# PADRÃO COMMAND: Importação das classes do padrão
# - Command: Interface base que define o método execute()
# - Comandos específicos: Cada ação do menu encapsulada em uma classe própria
from .commands import (
    Command,
    ShowProfileCommand,
    CreateSiteCommand,
    SelectSiteCommand,
    ShowUserSitesCommand,
    ShowLogsCommand
)

class LoggedMenu(AbstractMenu):
    logged_user: User

    def __init__(self, logged_user: User):
        self.logged_user = logged_user
        
        # PADRÃO COMMAND: Lista de comandos ao invés de funções
        # Cada opção do menu é agora um objeto Command que encapsula:
        # - A ação a ser executada (método execute())
        # - Os dados necessários (passados no construtor)
        # - A descrição da ação (atributo description)
        self.options: list[Command] = [
            ShowProfileCommand(self.logged_user, "Exibir dados de perfil"),
            CreateSiteCommand(self.logged_user, "Criar um site"),
            SelectSiteCommand(self.logged_user, "Selecionar um site"),
            ShowUserSitesCommand(self.logged_user, "Listar sites do usuário"),
        ]

        # PADRÃO COMMAND: Adição condicional de comando baseado em permissão
        # Comandos podem ser adicionados dinamicamente à lista
        if self.logged_user.role == UserRole.ADMIN:
            self.options.append(ShowLogsCommand("Ver logs do sistema"))

    def show(self):
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            print(f"CMS\nBem vindo, {self.logged_user.first_name}!\n")

            for i, command in enumerate(self.options):
                print(f"{i + 1}. {command.description}")
            print("0. Fazer logout")
            
            try:
                selected_index = int(input("\nDigite o número da opção para selecioná-la: "))
                if selected_index == 0:
                    break
                
                # PADRÃO COMMAND: Execução do comando selecionado
                # O menu não precisa saber os detalhes de como a ação é executada
                # Apenas chama execute() e o comando faz o resto
                # Isso promove baixo acoplamento e alta coesão
                command_to_execute = self.options[selected_index - 1]
                command_to_execute.execute()

            except (ValueError, IndexError):
                print("Opção inválida.")
                input("Clique Enter para tentar novamente.")