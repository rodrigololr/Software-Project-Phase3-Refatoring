from abc import ABC, abstractmethod
import os
import threading
from typing import Callable, TypeVar, TypedDict

from cms.repository import (
    AnalyticsRepository,
    CommentRepository,
    MediaRepository,
    PermissionRepository,
    PostRepository,
    SiteRepository,
    UserRepository,
)
from cms.services.languages import LanguageService
from cms.events import EventManager



# aplicar o sigleton aqui, parece encaixar bem
class AppContext:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # double-checked locking
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    # Cria a instância
                    inst = super(AppContext, cls).__new__(cls)
                    
                    inst.__event_manager = EventManager()
                    analytics_observer = AnalyticsRepository() # observador
                    
                    inst.__site_repo = SiteRepository()
                    inst.__post_repo = PostRepository()
                    inst.__user_repo = UserRepository()
                    inst.__comment_repo = CommentRepository()
                    inst.__media_repo = MediaRepository()
                    inst.__permission_repo = PermissionRepository()
                    inst.__lang_service = LanguageService()
                    
                    # atribui o observador criado à sua property
                    inst.__analytics_repo = analytics_observer
                    
                    # inscreve o Analytics para ouvir os eventos que importam
                    inst.__event_manager.subscribe("SITE_ACCESSED", analytics_observer)
                    inst.__event_manager.subscribe("POST_VIEWED", analytics_observer)
                    inst.__event_manager.subscribe("POST_COMMENTED", analytics_observer)
                    
                    cls._instance = inst
        return cls._instance

    @property
    def event_manager(self) -> EventManager:
        return self.__event_manager

    @property
    def analytics_repo(self) -> AnalyticsRepository:
        return self.__analytics_repo

    @property
    def site_repo(self) -> SiteRepository:
        return self.__site_repo

    @property
    def post_repo(self) -> PostRepository:
        return self.__post_repo

    @property
    def user_repo(self) -> UserRepository:
        return self.__user_repo

    @property
    def comment_repo(self) -> CommentRepository:
        return self.__comment_repo

    @property
    def media_repo(self) -> MediaRepository:
        return self.__media_repo

    @property
    def permission_repo(self) -> PermissionRepository:
        return self.__permission_repo

    @property
    def lang_service(self) -> LanguageService:
        return self.__lang_service

    def reset_context(self):
        self.__event_manager = EventManager()
        analytics_observer = AnalyticsRepository() # observador
        self.__site_repo = SiteRepository()
        self.__post_repo = PostRepository()
        self.__user_repo = UserRepository()
        self.__media_repo = MediaRepository()
        self.__comment_repo = CommentRepository()
        self.__analytics_repo = AnalyticsRepository()
        self.__permission_repo = PermissionRepository()
        self.__lang_service = LanguageService()
