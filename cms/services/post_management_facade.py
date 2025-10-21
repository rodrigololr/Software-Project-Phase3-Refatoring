from cms.services.post_builder import PostBuilder
from cms.models import Post, Site, User, SiteAnalyticsEntry, SiteAction
from cms.context import AppContext


class PostManagementFacade:
    """Fachada que simplifica a criação e registro de posts."""

    def __init__(self, context: AppContext):
        self.__context = context

    def create_and_register_post(self, site: Site, user: User) -> Post:
        """Encapsula todo o fluxo: construir + salvar + logar analytics."""
        
        builder = PostBuilder(site, user)
        post = (builder.set_language()
                       .set_title()
                       .add_content_blocks()
                       .set_schedule_date()
                       .build())

        self.__context.post_repo.add_post(post)
        
        self.__context.analytics_repo.log(
            SiteAnalyticsEntry(
                user=user,
                site=site,
                action=SiteAction.CREATE_POST,
                metadata={"post_id": str(post.id)}
            )
        )

        return post
