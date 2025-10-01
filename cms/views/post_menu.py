from cms.models import Comment, Post, PostAction, PostAnalyticsEntry, Site, User
from cms.services.post_translator import PostTranslator
from cms.services.seo_analyzier import display_seo_report
from cms.services.social_media import (
    SocialMedia,
    build_social_media_post,
    get_social_media_poster,
)
from cms.utils import select_enum
from cms.views.menu import AbstractMenu, AppContext, MenuOptions, clear_screen


class PostMenu(AbstractMenu):
    logged_user: User
    selected_site: Site
    selected_post: Post

    # construtor simplificado
    def __init__(
        self,
        logged_user: User,
        selected_site: Site,
        selected_post: Post,
    ):
        self.logged_user = logged_user
        self.selected_site = selected_site
        self.selected_post = selected_post

    def show(self):
        self.selected_post_language = self.selected_post.default_language

        options: list[MenuOptions] = [
            {"message": "Mostrar comentários do post",
                "function": self._show_post_comments},
            {"message": "Comentar no post", "function": self._comment_on_post},
            {"message": "Trocar idioma do post",
                "function": self._change_post_language},
            {"message": "Sugestão de estrutura para comparilhamento em redes sociais",
                "function": self._sharing_suggestion},
        ]

        # acessa repo de permissões via Singleton
        if AppContext().permission_repo.has_permission(
            self.logged_user, self.selected_site
        ):
            options.extend(
                [
                    {"message": "Traduzir post", "function": self._translate_post},
                    {"message": "Ver estatísticas do post",
                        "function": self._show_post_analytics},
                    {"message": "Ver relatório de análise de SEO",
                        "function": self._show_seo_report},
                ]
            )

        def display_title():
            self.selected_post.display_post(self.selected_post_language)

        PostMenu.prompt_menu_option(options, display_title)

    def _show_post_comments(self):
        post_comments: list[Comment] = AppContext(
        ).comment_repo.get_post_comments(self.selected_post)

        for comment in post_comments:
            print(comment.body)
            print(f"{comment.commenter.username} @ {comment.created_at}")
            print(" ")

        input("\nClique Enter para voltar ao Menu.")

    def _comment_on_post(self):
        body = input("Digite seu comentário: ")
        comment = Comment(post=self.selected_post,
                          commenter=self.logged_user, body=body)

        context = AppContext()
        context.comment_repo.add_comment(comment)
        context.analytics_repo.log(
            PostAnalyticsEntry(
                user=self.logged_user,
                site=self.selected_site,
                post=self.selected_post,
                action=PostAction.COMMENT,
                metadata={"comment_id": str(comment.id)},
            )
        )

    def _change_post_language(self):
        languages = self.selected_post.get_languages()
        if len(languages) == 1:
            clear_screen()
            input(
                f"O Post só tem uma linguagem: {languages[0]}. Clique enter para voltar.")
            return

        # singleton!
        self.selected_post_language = AppContext().lang_service.select_language(languages)

    def _sharing_suggestion(self):
        print("Esta ferramenta te ajuda a estruturar seu Post para")
        print("compartilhamento em redes sociais.")

        print("\nPara obter sugestões, escolha o idioma do Post e a rede social.")
        languages = self.selected_post.get_languages()
        if len(languages) == 1:
            language = languages[0]
        else:
            # escolha a lingua (usando singleton)
            language = AppContext().lang_service.select_language(languages)
            if not language:
                input(
                    "Não é possível continuar sem escolher um idioma. "
                    "Clique Enter para voltar"
                )
                return

        print(" ")

        social_media = select_enum(SocialMedia, "Selecione uma rede social: ")
        if not social_media:
            input(
                "Não é possível continuar sem escolher uma Rede Social. "
                "Clique Enter para voltar"
            )
            return

        clear_screen()

        print(f"Post: {self.selected_post.get_default_title()}")
        print(f"Idioma: {language}")
        print(f"Rede Social: {social_media}")

        # pede para a fábrica a "máquina" correta
        poster_factory = get_social_media_poster(social_media)
        # manda a máquina criar o post
        social_post = poster_factory.create_post(self.selected_post, language)

        social_post.display_sharing_suggestion()

        input("\nRecomendação finalizada. Clique Enter para voltar.")

    def _translate_post(self):
        pt = PostTranslator(self.selected_post)
        pt.translate()

    def _show_post_analytics(self):
        # singleton!!!!!
        analytics_repo = AppContext().analytics_repo
        views = analytics_repo.get_post_views(self.selected_post.id)
        shares = analytics_repo.get_post_shares(self.selected_post.id)
        comments = analytics_repo.get_post_comments(self.selected_post.id)

        self.selected_post.display_post_short()
        print(f"Visualizações: {views}")
        print(f"Comentários: {comments}")
        print(f"Compartilhamentos: {shares}")
        input("\nClique Enter para voltar ao Menu.")

    def _show_seo_report(self):
        languages = self.selected_post.get_languages()
        if len(languages) == 1:
            language = languages[0]
        else:
            # singleton!
            language = AppContext().lang_service.select_language(languages)
            if not language:
                return

        display_seo_report(self.selected_post, language)
        input("Clique Enter para voltar ao menu.")
