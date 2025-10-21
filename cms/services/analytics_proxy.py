from cms.repository import AnalyticsRepository
from cms.models import User, UserRole, AnalyticsEntry, Site


class AnalyticsRepositoryProxy(AnalyticsRepository):
    """Proxy que controla acesso ao repositório de analytics com verificação de permissoes"""

    def __init__(self, real_repo: AnalyticsRepository, current_user: User, permission_repo):
        self.__real_repo = real_repo
        self.__current_user = current_user
        self.__permission_repo = permission_repo

    def _check_access_to_site(self, site_id: int) -> None:
        # Verifica se o usuário tem acesso ao site para ver analytics.
        if self.__current_user.role == UserRole.ADMIN:
            return

        site_entry = next(
            (entry for entry in self.__real_repo._AnalyticsRepository__entries.values()
             if hasattr(entry, 'site') and entry.site.id == site_id),
            None
        )

        if site_entry:
            site = site_entry.site
            if not self.__permission_repo.has_permission(self.__current_user, site):
                raise PermissionError(
                    f"Acesso negado: você não tem permissão para ver analytics do site {site.id}"
                )

    def get_site_accesses(self, site_id: int) -> int:
        self._check_access_to_site(site_id)
        return self.__real_repo.get_site_accesses(site_id)

    def get_site_post_creation_count(self, site_id: int) -> int:
        self._check_access_to_site(site_id)
        return self.__real_repo.get_site_post_creation_count(site_id)

    def get_site_media_upload_count(self, site_id: int) -> int:
        self._check_access_to_site(site_id)
        return self.__real_repo.get_site_media_upload_count(site_id)

    def get_site_total_post_views(self, site_id: int) -> int:
        self._check_access_to_site(site_id)
        return self.__real_repo.get_site_total_post_views(site_id)

    def get_site_total_post_shares(self, site_id: int) -> int:
        self._check_access_to_site(site_id)
        return self.__real_repo.get_site_total_post_shares(site_id)

    def get_site_total_post_comments(self, site_id: int) -> int:
        self._check_access_to_site(site_id)
        return self.__real_repo.get_site_total_post_comments(site_id)

    def get_post_views(self, post_id: int) -> int:
        return self.__real_repo.get_post_views(post_id)

    def get_post_shares(self, post_id: int) -> int:
        return self.__real_repo.get_post_shares(post_id)

    def get_post_comments(self, post_id: int) -> int:
        return self.__real_repo.get_post_comments(post_id)

    def log(self, entry: AnalyticsEntry) -> int:
        return self.__real_repo.log(entry)

    def show_logs(self, limit: int = 5) -> None:
        if self.__current_user.role != UserRole.ADMIN:
            raise PermissionError("Apenas admins podem ver logs do sistema.")
        self.__real_repo.show_logs(limit)
