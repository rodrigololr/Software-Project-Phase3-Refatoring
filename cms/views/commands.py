import os
from abc import ABC, abstractmethod
from cms.models import User, UserRole, Site, Permission, SiteAction, SiteAnalyticsEntry
from cms.context import AppContext
from cms.views.site_menu import SiteMenu
from cms.views.menu import AbstractMenu
from cms.exceptions import ValidationError, RepositoryError, OperationFailedError, CMSException


class Command(ABC):
    """A interface para todos os comandos."""
    def __init__(self, description: str):
        self.description = description

    @abstractmethod
    def execute(self):
        pass

class ShowProfileCommand(Command):
    """Comando para exibir o perfil do usuário."""
    def __init__(self, user: User, description: str):
        super().__init__(description)
        self.user = user

    def execute(self):
        try:
            print(f"Nome: {self.user.first_name} {self.user.last_name}")
            print(f"E-mail: {self.user.email}")
            print(f"Role: {self.user.role.name}")
            input("\nClique Enter para voltar ao Menu.")
        except CMSException as e:
            print(f"Erro ao exibir perfil: {str(e)}")
            input("Clique Enter para voltar.")

class CreateSiteCommand(Command):
    """Comando para criar um novo site."""
    def __init__(self, user: User, description: str):
        super().__init__(description)
        self.user = user

    def execute(self):
        try:
            # coleta dados do novo site
            site_name = input("Diga o nome do seu site: ").strip()
            if not site_name:
                raise ValidationError("Nome do site não pode estar vazio.")
            
            site_description = input("Informe uma descrição breve para o site: ").strip()
            if not site_description:
                raise ValidationError("Descrição do site não pode estar vazia.")
            
            site = Site(owner=self.user, name=site_name, description=site_description)
            
            context = AppContext()
            context.site_repo.add_site(site)
            permission = Permission(user=self.user, site=site)
            context.permission_repo.grant_permission(permission)
            
            print("Site criado com sucesso!")
            input("Clique Enter para voltar ao menu.")
            
        except ValidationError as e:
            print(f"Erro de validação: {e}")
            input("Clique Enter para voltar.")
        except CMSException as e:
            print(f"Erro ao criar site: {str(e)}")
            input("Clique Enter para voltar.")

class SelectSiteCommand(Command):
    """Comando para listar e selecionar um site."""
    def __init__(self, user: User, description: str):
        super().__init__(description)
        self.user = user

    def execute(self):
        try:
            sites: list[Site] = AppContext().site_repo.get_sites()

            def execute_for_option(selected_site: Site):
                try:
                    # aqui dispara o evento em vez de logar diretamente
                    AppContext().event_manager.notify(
                        "SITE_ACCESSED",
                        user=self.user,
                        site=selected_site
                    )
                    SiteMenu(self.user, selected_site).show()
                except CMSException as e:
                    print(f"Erro ao acessar site: {str(e)}")
                    input("Clique Enter para voltar.")

            AbstractMenu.prompt_generic(
                sites, "Sites disponíveis", execute_for_option, lambda m: m.name
            )
        except CMSException as e:
            print(f"Erro ao listar sites: {str(e)}")
            input("Clique Enter para voltar.")

class ShowUserSitesCommand(Command):
    """Comando para listar os sites que o usuário possui."""
    def __init__(self, user: User, description: str):
        super().__init__(description)
        self.user = user

    def execute(self):
        try:
            user_sites: list[Site] = AppContext().site_repo.get_user_sites(self.user)
            if not user_sites:
                print("Você ainda não criou nenhum site.")
            else:
                print("Estes são os sites que você criou:")
                for i, site in enumerate(user_sites):
                    print(f"{i + 1}. {site.name}")
            
            input("\nClique Enter para voltar ao Menu.")
        except CMSException as e:
            print(f"Erro ao listar sites: {str(e)}")
            input("Clique Enter para voltar.")

class ShowLogsCommand(Command):
    """Comando (apenas para Admin) para ver os logs do sistema."""
    def __init__(self, description: str):
        super().__init__(description)

    def execute(self):
        try:
            os.system('clear' if os.name == 'posix' else 'cls')
            
            while True:
                try:
                    limit_input = input("Insira a quantidade de logs que deseja ver (ou 0 para voltar): ").strip()
                    
                    if not limit_input:
                        raise ValidationError("Entrada não pode estar vazia.")
                    
                    limit = int(limit_input)
                    
                    if limit < 0:
                        raise ValidationError("O número deve ser positivo.")
                    
                    if limit == 0:
                        break
                    
                    AppContext().analytics_repo.show_logs(limit=limit)
                    break
                    
                except ValueError:
                    print("Valor inválido. Digite um número inteiro.")
                except ValidationError as e:
                    print(f"Erro: {e}")

            input("\nClique Enter para voltar ao menu.")
            
        except CMSException as e:
            print(f"Erro ao exibir logs: {str(e)}")
            input("Clique Enter para voltar.")