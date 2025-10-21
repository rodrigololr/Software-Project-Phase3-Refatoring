# Content Management System
Trata-se de um sistema de linha de comando em que o usuário pode criar e gerenciar sites de conteúdo. Em cada Site podem ser publicados (ou agendados) Posts. Em cada Post, pode-se fazer comentários. Cada Site também conta com uma biblioteca de Mídias que podem ser usadas para construção dos Posts. 

## Como executar
```python
python main.py
```

>[!warning]
> Desenvolvido e testado com Python `3.13`.

## Funcionalidades implementadas
- [x] User Roles and Permissions
- [x] Content Creation and Editing
- [x] Comment and Review System
- [x] Media Library Management
- [x] Content Scheduling
- [x] Analytics and Reporting
- [x] Template and Design Customization
- [x] SEO Optimization Tools
- [x] Multi-Language Support
- [x] Social Media Integration

## Projeto do Modelo do Sistema (Objetos)
- **User**: Represents an user in the system
- **Site**: Represents a website that an user (owner) can create and other users can access
- **Post**: Represents the information available to an User in a Site
- **Content**: Represents information of a Post in a language. It is a list of ContentBlocks.
- **ContentBlock**: Represents a fraction of the information of a Post
- **TextBlock**: Represents a block of text that is part of a Post 
- **MediaBlock**: Represents a block containing a Media file that is part of a Post
- **CarouselBlock**: Represents a carousel of Medias thath can be placed in the Post body
- **MediaFile**: Represents a Media file and all their metadata (width, height, size in bytes, etc)
- ~~**VideoFile**: Represents a video file and their specific data~~
- ~~**ImageFile**: Represents an image file and their specific data~~
    - These subclasses are not really necessary, because there are not enough differences between them. The MediaFile class alone will suffice for this application. 
- **Permission**: Represents which Post/Site an User can access
- **Comment**: Represents a message that a User can leave on a Post
- **AnalyticsEntry**: Represents an action of an User that will be used to extract metrics
- **AnalyticsReport**: Represents a closed snapshot of metrics to present
- **SiteAnalyticsReport**: Represents a AnalyticsReport for a Site 
- **PostAnalyticsReport**: Represents a AnalyticsReport for a Post
- **Template**: Represents the way the a Site will be presented to the User
- **Language**: Represents a language that a User can write a Post or a Comment in
- **SocialMedia**: Represents a Social Media to which the User can share a Post
- **SocialMediaPost**: Represents the Post formatted to that Social Media.
- **FacebookPost** Represents the Post formatted to be Posted in Facebook. 
- **InstagramPost** Represents the Post formatted to be Posted in Instagram. 
- **TwitterPost** Represents the Post formatted to be Posted in Instagram. 


## Padrões de Projeto Comportamentais


#### 1. Strategy (Estratégia)

* **O que é?**: é um padrão de projeto comportamental que permite que você defina uma família de algoritmos, coloque-os em classes separadas, e faça os objetos deles intercambiáveis.
* **Aplicação no Projeto**: Este padrão é utilizado no sistema de templates de site (`cms/services/site_template.py`). Cada classe de template (`LatestPostsTemplate`, `TopPostsFirstTemplate`, ...) é uma **estratégia** diferente para selecionar e ordenar os posts que serão exibidos. O `SiteMenu` utiliza a estratégia que está configurada no objeto `Site`, podendo trocá-la a qualquer momento, alterando dinamicamente como o conteúdo é apresentado.

#### 2. Command (Comando)

* **O que é?**: O padrão Command transforma uma solicitação em um objeto autônomo que contém todas as informações sobre a solicitação. Isso permite parametrizar clientes com diferentes solicitações, enfileirar ou registrar solicitações e suportar operações que podem ser desfeitas.
* **Aplicação no Projeto**: O padrão foi usado para refatorar o sistema de menus implementei no `LoggedMenu`. Em vez de o menu chamar diretamente as funções, cada opção do menu é agora um objeto **Comando**. O menu simplesmente mantém uma lista desses comandos e executa o que for selecionado pelo usuário. Isso desacopla o menu da lógica das ações, tornando o sistema mais extensível e organizado.


### 3. Observer (Observador)
* **O que é?**: O padrão Observer define uma dependência um-para-muitos entre objetos, de modo que quando um objeto muda de estado, todos os seus dependentes são notificados e atualizados automaticamente.
* **Aplicação no Projeto**: Este padrão foi implementado para desacoplar o sistema de `Analytics` do restante da aplicação. Antes, os menus e comandos precisavam chamar diretamente o `analytics_repo.log()` para registrar uma ação. Agora, eles apenas disparam um evento `(ex: "POST_VIEWED")`. O `AnalyticsRepository`` atua como um Observador, que "escuta" esses eventos e reage criando o log correspondente. Dessa forma, os menus não precisam saber que o sistema de analytics existe, tornando o código mais flexível e fácil de manter.


## Padrões de Projeto Criacionais

#### 1. Factory Method (Método de Fábrica)

* **O que é?**: O padrão Factory Method define uma interface para criar um objeto, mas deixa as subclasses decidirem qual classe instanciar. Isso permite adiar a instanciação para subclasses.
* **Aplicação no Projeto**: Este padrão foi implementado no sistema de redes sociais (`cms/services/social_media.py`). A classe abstrata `SocialMediaPoster` atua como o creator, enquanto subclasses concretas como `FacebookPoster`, `InstagramPoster` e `TwitterPoster` implementam o método `factory_method()` que retorna a classe de post apropriada (`FacebookPost`, `InstagramPost`, `TwitterPost`). Isso permite que novos tipos de redes sociais sejam adicionados sem modificar o código existente, apenas criando novas subclasses de `SocialMediaPoster`.

#### 2. Singleton (Instância Única)

* **O que é?**: O padrão Singleton garante que uma classe tenha apenas uma instância e fornece um ponto global de acesso a essa instância.
* **Aplicação no Projeto**: O padrão Singleton foi implementado no `AnalyticsRepository` para garantir que haja apenas uma instância desse repositório em toda a aplicação. Isso é importante porque o `AnalyticsRepository` é responsável por coletar e armazenar dados analíticos, e ter múltiplas instâncias poderia levar a inconsistências nos dados.

#### 3. Builder (Construtor)
* **O que é?**: O padrão Builder separa a construção de um objeto complexo da sua representação, permitindo que o mesmo processo de construção crie diferentes representações.
* **Aplicação no Projeto**: Este padrão foi aplicado na criação de objetos `Post` no `PostRepository`. O `PostBuilder` permite construir um `Post` passo a passo, configurando diferentes atributos como título, conteúdo, mídia associada, etc. Isso facilita a criação de posts complexos e melhora a legibilidade do código, especialmente quando há muitos atributos opcionais.


## Padrões de Projeto Estruturais

#### 1. Proxy (Procurador)

* **O que é?**: O padrão Proxy fornece um objeto substituto ou marcador de posição para outro objeto. Um proxy controla o acesso ao objeto real, permitindo adicionar lógica antes ou depois de delegação.
* **Aplicação no Projeto**: Este padrão foi implementado em `cms/services/analytics_proxy.py` com a classe `AnalyticsRepositoryProxy`. O proxy atua como intermediário entre as views/menu e o `AnalyticsRepository` real, verificando permissões antes de permitir acesso aos dados. ADMINs podem acessar analytics de qualquer site, enquanto USERs só podem acessar dados de sites nos quais têm permissão. Operações como `show_logs()` (visão geral do sistema) são restritas apenas a ADMINs. Se um acesso não autorizado for tentado, o proxy lança uma `PermissionError`, protegendo dados sensíveis.



