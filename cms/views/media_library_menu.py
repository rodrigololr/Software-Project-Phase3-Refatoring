# cms/views/media_library_menu.py

from pathlib import Path
from cms.models import MediaFile, Site, SiteAction, SiteAnalyticsEntry, User
from cms.utils import infer_media_type
from cms.views.media_detail_menu import MediaMenu
from cms.views.menu import AbstractMenu, MenuOptions
from cms.context import AppContext
from cms.exceptions import ValidationError, MediaError, ResourceNotFoundError


class MediaLibraryMenu(AbstractMenu):
    logged_user: User
    selected_site: Site

    def __init__(self, logged_user: User, selected_site: Site):
        self.logged_user = logged_user
        self.selected_site = selected_site
        # keep a reference to the shared application context (singleton)
        self.context = AppContext()

    def show(self):
        # singleton!
        if not self.context.permission_repo.has_permission(
            self.logged_user, self.selected_site
        ):
            return

        options: list[MenuOptions] = [
            {"message": "Importar nova mídia", "function": self._import_media},
            {"message": "Listar mídias", "function": self._select_media},
        ]

        MediaLibraryMenu.prompt_menu_option(
            options,
            lambda: print(
                f"Biblioteca de mídias do site {self.selected_site.name}\n"),
        )

    def _import_media(self):
        try:
            filepath = input(
                "Digite o caminho completo do arquivo de mídia a ser importado:\n> "
            ).strip()

            if not filepath:
                print("Nenhum caminho informado.")
                input("Clique Enter para voltar.")
                return

            path = Path(filepath)

            if not path.exists():
                raise ValidationError("Arquivo não encontrado. Verifique o caminho digitado.")

            filename = path.name

            try:
                media_type = infer_media_type(path.suffix)
            except (ValidationError, MediaError) as e:
                print(f"Erro: {e}")
                input("Clique Enter para voltar.")
                return

            media = MediaFile(
                uploader=self.logged_user,
                filename=filename,
                path=path,
                media_type=media_type,
                site=self.selected_site,
                width="1000",
                height="1000",
                duration=None,
            )

            context = AppContext()
            media_id = context.media_repo.add_midia(media)
            print(f"Mídia importada com id {media_id}.")

            context.analytics_repo.log(
                SiteAnalyticsEntry(
                    user=self.logged_user,
                    site=self.selected_site,
                    action=SiteAction.UPLOAD_MEDIA,
                )
            )

            input("Clique Enter para voltar ao menu.")
            
        except ValidationError as e:
            print(f"Erro de validação: {e}")
            input("Clique Enter para voltar.")
        except Exception as e:
            print(f"Erro ao importar mídia: {str(e)}")
            input("Clique Enter para voltar.")

    def _select_media(self):
        try:
            # singleton!
            medias: list[MediaFile] = AppContext().media_repo.get_site_medias(
                self.selected_site
            )

            if not medias:
                print("Nenhuma mídia encontrada para este site.")
                input("Clique Enter para voltar ao menu.")
                return

            def execute_for_option(selected_media: MediaFile):
                try:
                    MediaMenu(selected_media).show()
                except Exception as e:
                    print(f"Erro ao abrir mídia: {str(e)}")
                    input("Clique Enter para voltar.")

            MediaLibraryMenu.prompt_generic(
                medias,
                f"Mídias do site {self.selected_site.name}\n",
                execute_for_option,
                lambda m: m.filename,
            )
            
        except Exception as e:
            print(f"Erro ao listar mídias: {str(e)}")
            input("Clique Enter para voltar.")
