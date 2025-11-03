---
marp: true
theme: default
size: 16:9
style: |
  section { font-size: 18px; padding: 40px; }
  h1 { font-size: 54px; }
  h2 { font-size: 44px; }
  code { font-size: 24px; background: #f0f0f0; padding: 2px 6px; }
  pre { font-size: 24px; }
---

# Padrões de Projeto
## Comportamentais e Estruturais

---

# Padrões Comportamentais

---

## 1. Strategy

**O que é?** Um padrão que permite trocar o **algoritmo** (forma de fazer algo) sem modificar o código que o usa.

**Analogia:** Diferentes formas de ordenar posts: por data, por visualizações, por comentários. Cada forma é uma "estratégia".

**Onde está:** `cms/services/site_template.py` e `cms/models/__init__.py`

**Meu código:**
```python
# Site tem um template configurável
@dataclass
class Site:
    template: SiteTemplateType = SiteTemplateType.LATEST_POSTS

# Diferentes estratégias de exibição
class LatestPostsTemplate(SiteTemplate):
    def select_posts(self):
        return sorted(posts, key=lambda p: p.created_at, reverse=True)

class TopPostsFirstTemplate(SiteTemplate):
    def select_posts(self):
        return sorted(posts, key=lambda p: views_count, reverse=True)

# Usuário troca o template sem alterar código
site.template = SiteTemplateType.TOP_POSTS_FIRST

# Por quê? Diferentes layouts de site sem reescrever lógica, apenas troca de estratégia.







```

---

## 2. Command (Parte 1)

**O que é?** Um padrão que encapsula uma **ação/solicitação** em um objeto para executá-la depois ou registrá-la.

**Analogia:** Em vez de chamar funções diretamente, você cria objetos que **sabem como fazer** a ação e os chama depois.

**Onde está:** `cms/views/commands.py` e `cms/views/logged_menu.py`

**Interface:**
```python
class Command(ABC):
    def __init__(self, description: str):
        self.description = description
    
    @abstractmethod
    def execute(self): pass
```

---

## 2. Command (Parte 2)

**Meu código em uso:**
```python
# Em LoggedMenu - lista de comandos em vez de funções
self.options: list[Command] = [
    ShowProfileCommand(user, "Exibir dados de perfil"),
    CreateSiteCommand(user, "Criar um site"),
    SelectSiteCommand(user, "Selecionar um site"),
]

# Execução
for command in self.options:
    print(f"{i}. {command.description}")
if user_choice:
    self.options[choice].execute()  # Executa quando necessário
```

**Por quê?** Menu não precisa saber detalhes. Adiciona/remove comandos facilmente.

---

## 3. Observer (Parte 1)

**O que é?** Um padrão onde objetos **observadores** se inscrevem para ser **notificados automaticamente** quando algo importante acontece.

**Analogia:** Você se inscreve em um canal do YouTube. Quando há novo vídeo, o YouTube te notifica automaticamente.

**Onde está:** `cms/events.py` e `cms/repository.py`

**Sistema de eventos:**
```python
# EventManager gerencia inscrições
class EventManager:
    def subscribe(self, event_type: str, observer: Observer):
        # Observer se inscreve para um tipo de evento
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(observer)
    
    def notify(self, event_type: str, **kwargs):
        # Notifica todos os observadores
        for observer in self._subscribers[event_type]:
            observer.update(event_type, **kwargs)
```

---

## 3. Observer (Parte 2)

**Meu código em uso:**
```python
# Em commands.py - quando usuário acessa site
AppContext().event_manager.notify(
    "SITE_ACCESSED",
    user=self.user,
    site=selected_site
)

# Em AnalyticsRepository - recebe notificação automática
def update(self, event_type: str, **kwargs):
    if event_type == "SITE_ACCESSED":
        entry = SiteAnalyticsEntry(
            user=kwargs.get('user'),
            site=kwargs.get('site'),
            action=SiteAction.ACCESS
        )
        self.log(entry)  # Registra o acesso
```

**Por quê?** Menu dispara evento. Analytics "escuta" e registra. Sem acoplamento!

---

# Padrões Estruturais

---

## 1. Proxy (Parte 1)

**O que é?** Um padrão que coloca um **intermediário** para controlar e validar o acesso a um objeto real.

**Analogia:** Um segurança na porta validando documentos antes de deixar entrar. Admin = entra em tudo. Usuário = só em seus sites.

**Onde está:** `cms/services/analytics_proxy.py` e `cms/context.py`

**Interface do Proxy:**
```python
class AnalyticsRepositoryProxy(AnalyticsRepository):
    def __init__(self, real_repo, current_user, permission_repo):
        self.__real_repo = real_repo  # O objeto real
        self.__current_user = current_user
        self.__permission_repo = permission_repo
    
    def _check_access_to_site(self, site_id: int):
        if self.__current_user.role == UserRole.ADMIN:
            return  # Admin passa
        if not self.__permission_repo.has_permission(user, site):
            raise PermissionError("Acesso negado")  # Bloqueia
```

---

## 1. Proxy (Parte 2)

**Meu código em uso:**
```python
# Todos os métodos fazem a validação antes
def get_site_accesses(self, site_id: int):
    self._check_access_to_site(site_id)  # Valida permissão
    return self.__real_repo.get_site_accesses(site_id)  # Chama real

# Em AppContext - fornece o proxy em vez do real
def get_protected_analytics(self, user):
    return AnalyticsRepositoryProxy(
        self.__analytics_repo,  # O repositório real
        user,
        self.__permission_repo
    )
```

**Por quê?** Proteção automática. Admin vê tudo, usuários só seus dados.

---

## 2. Facade (Parte 1)

**O que é?** Um padrão que oferece uma **interface simples** para um subsistema complexo com múltiplos componentes.

**Analogia:** Um garçom no restaurante. Você pede um prato (uma linha) e ele coordena cozinheiro, copeiro, etc (múltiplos serviços).

**Onde está:** `cms/services/post_management_facade.py`

**Classe Facade:**
```python
class PostManagementFacade:
    def __init__(self, context, notification_adapter=None):
        self.__context = context  # Acesso a todos os serviços
        self.__notification_adapter = (
            notification_adapter or ConsoleNotificationAdapter()
        )
    
    def create_and_register_post(self, site: Site, user: User):
        # Uma chamada faz tudo!
        builder = PostBuilder(site, user)
        post = (builder.set_language()
                       .set_title()
                       .add_content_blocks()
                       .set_schedule_date()
                       .build())
```

---

## 2. Facade (Parte 2)
**Meu código em uso:**
```python
# Continuação - Facade encapsula:
        self.__context.post_repo.add_post(post)  # Salva
        
        self.__context.analytics_repo.log(
            SiteAnalyticsEntry(
                user=user, site=site,
                action=SiteAction.CREATE_POST
            )
        )
        
        self.__notification_adapter.notify(
            user, f"Post criado: {post.get_default_title()}!"
        )
        return post

# Em SiteMenu - super simples!
def _create_site_post(self):
    facade = PostManagementFacade(AppContext())
    post = facade.create_and_register_post(
        self.selected_site, self.logged_user)

# Por quê? Encapsula Builder + Repository + Analytics em uma chamada.

```


---

## 3. Adapter (Parte 1)

**O que é?** Um padrão que **adapta** a interface de uma classe para outra que o cliente espera. Conecta incompatíveis.

**Analogia:** Um adaptador de tomada. Você tem um plugue europeu e uma tomada americana. O adaptador conecta os dois.

**Onde está:** `cms/services/notification_adapter.py`

**Interface e implementações:**
```python
# Interface comum que todas devem seguir
class NotificationAdapter(ABC):
    @abstractmethod
    def notify(self, user: User, message: str): pass

# Diferentes formas de notificar
class ConsoleNotificationAdapter(NotificationAdapter):
    def notify(self, user, message):
        print(f" Notificação para {user.first_name}: {message}")

class EmailNotificationAdapter(NotificationAdapter):
    def notify(self, user, message):
        print(f"📧 E-mail enviado para {user.email}")
```

---

## 3. Adapter (Parte 2)

**Meu código em uso:**
```python
# Em PostManagementFacade - usa qualquer adapter
class PostManagementFacade:
    def __init__(self, context, notification_adapter=None):
        # Se não passar adapter, usa console
        self.adapter = notification_adapter or ConsoleNotificationAdapter()
    
    def create_and_register_post(self, site, user):
        post = ...
        # Não importa qual adapter é, chama igual
        self.adapter.notify(
            user, f"Post '{post.title}' criado no site '{site.name}'!"
        )
        return post
```

**Por quê?** Trocar console → email → SMS sem alterar Facade. Máximo desacoplamento!

---

# Resumo

| Tipo | Padrão | Objetivo |
|------|--------|----------|
| **Comportamental** | Strategy | Diferentes algoritmos intercambiáveis |
| **Comportamental** | Command | Encapsular solicitações como objetos |
| **Comportamental** | Observer | Notificações de mudanças |
| **Estrutural** | Proxy | Controlar acesso com permissões |
| **Estrutural** | Facade | Simplificar interface complexa |
| **Estrutural** | Adapter | Integrar interfaces incompatíveis |

---

