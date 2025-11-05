from datetime import datetime
from cms.utils import read_datetime_from_cli
from cms.services.languages import LanguageService
from cms.models import (
    Site,
    User,
    MediaFile,
    ContentBlock,
    TextBlock,
    MediaBlock,
    Post,
    Content,
    Language,
)
from cms.repository import MediaRepository
from cms.context import AppContext
from cms.exceptions import ValidationError, ResourceNotFoundError, CMSException


class PostBuilder:
    """
    implementação do padrão builder para construir um objeto post passo a passo
    """
    def __init__(self, site: Site, poster: User):
        self.__site = site
        self.__poster = poster
        # primeiro o biulder recebe as depedencias do singleton (appcontext)
        self.__media_repo = AppContext().media_repo
        self.__lang_service = AppContext().lang_service
        self.reset()

    def reset(self):
        """
        reseta o estado do builder para permitir a construção de um novo post
        sem interferência do anterior.
        """
        self.__language: Language | None = None
        self.__title: str = ""
        self.__blocks: list[ContentBlock] = []
        self.__scheduled_to: datetime = datetime.now()
        return self

    def set_language(self) -> 'PostBuilder':
        """
        parte 1: define o idioma do post
        """
        self.__language = self.__lang_service.select_from_supported_languages()
        if not self.__language:
            raise ValueError("A linguagem é obrigatória para criar um post.")
        return self

    def set_title(self) -> 'PostBuilder':
        """
        parte 2: define o título do post
        """
        try:
            self.__title = input("Digite o título do post: ").strip()
            if not self.__title:
                raise ValidationError("O título não pode estar vazio.")
            return self
        except ValidationError:
            raise
        except CMSException as e:
            raise ValidationError(f"Erro ao definir título: {str(e)}")

    def add_content_blocks(self) -> 'PostBuilder':
        """
        parte 3: adiciona os blocos de conteúdo (texto, mídia) que formarão
        o corpo do post
        """
        try:
            order_counter = 1
            while True:
                print("\nSelecione o tipo de conteúdo para o corpo do post:")
                print("1. Bloco de Texto")
                print("2. Bloco de Mídia")
                print("0. Finalizar e continuar")
                try:
                    block_option = int(input("Opção: "))
                except ValueError:
                    print("Opção inválida. Tente novamente.")
                    continue

                if block_option == 0:
                    break
                elif block_option == 1:
                    text = input("Digite o conteúdo do bloco de texto: ").strip()
                    if not text:
                        print("Texto não pode estar vazio.")
                        continue
                    self.__blocks.append(TextBlock(order=order_counter, text=text))
                    order_counter += 1
                    print("✅ Bloco de texto adicionado.")
                elif block_option == 2:
                    media = self.__select_media_from_library()
                    if media:
                        alt = input("Digite o texto alternativo (alt) para a mídia: ").strip()
                        if not alt:
                            print("Texto alternativo não pode estar vazio.")
                            continue
                        self.__blocks.append(MediaBlock(order=order_counter, media=media, alt=alt))
                        order_counter += 1
                        print("Bloco de mídia adicionado.")
                else:
                    print("Opção inválida. Tente novamente.")
            return self
            
        except CMSException as e:
            raise ValidationError(f"Erro ao adicionar blocos de conteúdo: {str(e)}")

    def set_schedule_date(self) -> 'PostBuilder':
        """
        parte 4: define uma data e hora futura para a publicação do post.
        """
        is_scheduled = input("\nDeseja agendar a publicação deste post? (s/n): ").strip().lower()
        if is_scheduled == "s":
            self.__scheduled_to = read_datetime_from_cli()
        return self

    def build(self) -> Post:
        """
        parte final: monta o objeto post com todas as partes configuradas
        e o retorna
        """
        if not self.__language or not self.__title:
            raise ValueError("Não foi possível construir o post. Título e Linguagem são obrigatórios.")

        # cria o objeto de conteúdo específico do idioma
        post_content = Content(
            title=self.__title,
            body=self.__blocks,
            language=self.__language,
        )

        # cria o objeto post principal
        post = Post(
            poster=self.__poster,
            site=self.__site,
            scheduled_to=self.__scheduled_to,
        )
        post.add_content(self.__language.code, post_content)

        # Retorna o produto final
        return post

    def __select_media_from_library(self) -> MediaFile | None:
        """
        Método privado auxiliar para encapsular a lógica de seleção de mídia.
        """
        try:
            medias = self.__media_repo.get_site_medias(self.__site)

            if not medias:
                input("Nenhuma mídia disponível neste site. Clique Enter para voltar.")
                return None

            while True:
                print("\nSelecione a mídia da biblioteca:")
                for i, media in enumerate(medias):
                    print(f"{i + 1}. {media.filename} ({media.media_type.name})")
                print("0. Cancelar seleção de mídia")
                try:
                    option = int(input("Opção: "))
                    if option == 0:
                        return None
                    if 1 <= option <= len(medias):
                        return medias[option - 1]
                    
                    print("Opção inválida. Tente novamente.\n")
                except ValueError:
                    print("Opção inválida. Por favor, digite um número.\n")
                    
        except CMSException as e:
            print(f"Erro ao selecionar mídia: {str(e)}")
            return None