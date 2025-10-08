import os
from abc import ABC, abstractmethod
from cms.models import User, UserRole, Site, Permission, SiteAction, SiteAnalyticsEntry
from cms.context import AppContext
from cms.views.site_menu import SiteMenu
from cms.views.menu import AbstractMenu # Usado para a função prompt_generic


class Command(ABC):
    """A interface para todos os comandos."""
    def __init__(self, description: str):
        self.description = description

class ShowProfileCommand(Command):
    """Comando para exibir o perfil do usuário."""
    
    def __init__(self, user: User, description: str):
        super().__init__(description)
        self.user = user

    def execute(self):
        print(f"Nome: {self.user.first_name} {self.user.last_name}")
        print(f"E-mail: {self.user.email}")
        print(f"Role: {self.user.role.name}")
        input("\nClique Enter para voltar ao Menu.")

class CreateSiteCommand(Command):
    """Comando para criar um novo site."""
    
    def __init__(self, user: User, description: str):
        super().__init__(description)
        self.user = user

    def execute(self):
        # coleta dados do novo site
        site_name = input("Diga o nome do seu site: ")
        site_description = input("Informe uma descrição breve para o site: ")
        site = Site(owner=self.user, name=site_name, description=site_description)
        
        context = AppContext()
        context.site_repo.add_site(site)
        permission = Permission(user=self.user, site=site)
        context.permission_repo.grant_permission(permission)
        input("Site criado. Clique Enter para voltar ao menu.")

class SelectSiteCommand(Command):
    """Comando para listar e selecionar um site."""
    def __init__(self, user: User, description: str):
        super().__init__(description)
        self.user = user

    def execute(self):
        sites: list[Site] = AppContext().site_repo.get_sites()

        def execute_for_option(selected_site: Site):
            AppContext().analytics_repo.log(
                SiteAnalyticsEntry(
                    user=self.user,
                    site=selected_site,
                    action=SiteAction.ACCESS,
                )
            )
            SiteMenu(self.user, selected_site).show()

        AbstractMenu.prompt_generic(
            sites, "Sites disponíveis", execute_for_option, lambda m: m.name
        )

class ShowUserSitesCommand(Command):
    """Comando para listar os sites que o usuário possui."""
    def __init__(self, user: User, description: str):
        super().__init__(description)
        self.user = user

    def execute(self):
        user_sites: list[Site] = AppContext().site_repo.get_user_sites(self.user)
        if not user_sites:
            print("Você ainda não criou nenhum site.")
        else:
            print("Estes são os sites que você criou:")
            for i, site in enumerate(user_sites):
                print(f"{i + 1}. {site.name}")
        
        input("\nClique Enter para voltar ao Menu.")

class ShowLogsCommand(Command):
    """Comando (apenas para Admin) para ver os logs do sistema."""
    def __init__(self, description: str):
        super().__init__(description)

    def execute(self):
        try:
            os.system('clear' if os.name == 'posix' else 'cls')
            limit = int(input("Insira a quantidade de logs que deseja ver (ou 0 para voltar): "))
            if limit > 0:
                AppContext().analytics_repo.show_logs(limit=limit)
        except ValueError:
            print("Valor inválido.")
        
        input("\nClique Enter para voltar ao menu.")