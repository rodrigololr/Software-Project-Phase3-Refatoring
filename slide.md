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

**O que é?** Define uma família de algoritmos, encapsulando cada um.

**Exemplo:**
```python
class SiteTemplate(ABC):
    @abstractmethod
    def render(self, site): pass

class ModernTemplate(SiteTemplate):
    def render(self, site):
        return "<modern>...</modern>"
```

**Onde utilizei:** `cms/services/site_template.py`

**Por quê?** Diferentes layouts de site sem alterar lógica principal.

---

## 2. Command

**O que é?** Encapsula uma solicitação como objeto.

**Exemplo:**
```python
class Command(ABC):
    @abstractmethod
    def execute(self): pass

class CreatePostCommand(Command):
    def execute(self):
        # lógica de criação
```

**Onde utilizei:** `cms/views/commands.py` + `LoggedMenu`

**Por quê?** Registrar, desfazer e fila de comandos de forma desacoplada.

---

## 3. Observer

**O que é?** Notifica múltiplos objetos sobre mudanças.

**Exemplo:**
```python
class EventManager:
    def subscribe(self, event_type, observer):
        self._subscribers[event_type].append(observer)
    
    def notify(self, event_type, data):
        for observer in self._subscribers[event_type]:
            observer.update(data)
```

**Onde utilizei:** `cms/events.py` + `AnalyticsRepository` como Observer

**Por quê?** Analytics registra mudanças sem acoplamento.

---

# Padrões Estruturais

---

## 1. Proxy

**O que é?** Controla acesso a outro objeto, adicionando lógica antes/depois.

**Exemplo:**
```python
class AnalyticsRepositoryProxy(AnalyticsRepository):
    def _check_access_to_site(self, site_id):
        if user.role != ADMIN:
            raise PermissionError()
        return self.__real_repo.get_site_accesses(site_id)
```

**Onde utilizei:** `cms/services/analytics_proxy.py`

**Por quê?** Proteger dados sensíveis com validação de permissões.

---

## 2. Facade

**O que é?** Interface simplificada para subsistema complexo.

**Exemplo:**
```python
# Antes: 15+ linhas
# Depois:
facade = PostManagementFacade(context)
post = facade.create_and_register_post(site, user)
```

**Onde utilizei:** `cms/services/post_management_facade.py` + integrado em `SiteMenu._create_site_post()`

**Por quê?** Simplificar fluxo de criação (Builder + Repository + Analytics).

---

## 3. Adapter

**O que é?** Permite colaboração entre interfaces incompatíveis.

**Exemplo:**
```python
class NotificationAdapter(ABC):
    def notify(self, user, message): pass

class ConsoleNotificationAdapter(NotificationAdapter):
    def notify(self, user, message):
        print(f"Notificação: {message}")
```

**Onde utilizei:** `cms/services/notification_adapter.py` + integrado em `PostManagementFacade`

**Por quê?** Desacoplar notificações - trocar de console para e-mail sem alterar código.

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

