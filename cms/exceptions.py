"""
Módulo de exceções customizadas para o CMS.

Define exceções específicas do sistema para tratamento de erros mais granular e significativo.
Permite que diferentes tipos de erro sejam tratados de maneiras apropriadas.
"""


class CMSException(Exception):
    """Exceção base para todos os erros do CMS."""
    pass


class ValidationError(CMSException):
    """
    Lançada quando dados de entrada não passam na validação.

    Exemplos:
    - Título de post vazio
    - Username já existente
    - Senha fraca
    - Email inválido
    - Caminho de arquivo inválido
    """
    pass


class InvalidNameError(ValidationError):
    """
    Lançada quando um nome de usuário/nome contém caracteres inválidos.

    Use esta exceção quando o campo de nome/username deve conter apenas letras
    (opcionalmente espaços e acentos), e caracteres numéricos ou símbolos forem
    fornecidos pelo usuário.
    """
    pass


class PermissionDeniedError(CMSException):
    """
    Lançada quando um usuário não tem permissão para executar uma ação.

    Exemplos:
    - Usuário tenta acessar analytics de um site sem permissão
    - Usuário tenta deletar mídia de outro usuário
    - Usuário não-admin tenta ver logs do sistema
    """
    pass


class ResourceNotFoundError(CMSException):
    """
    Lançada quando um recurso (usuário, post, site, etc) não existe.

    Exemplos:
    - Tentativa de acessar um post inexistente
    - Tentativa de deletar mídia que não existe
    - Usuário não encontrado no repositório
    """
    pass


class AuthenticationError(CMSException):
    """
    Lançada quando há erro na autenticação.

    Exemplos:
    - Credentials inválidas (username/password incorretos)
    - Falha ao validar token/sessão
    """
    pass


class MediaError(CMSException):
    """
    Lançada quando há erro ao processar mídia.

    Exemplos:
    - Arquivo de mídia não encontrado no caminho especificado
    - Tipo de arquivo não suportado
    - Erro ao fazer upload de mídia
    - Dimensões de imagem inválidas
    """
    pass


class LanguageError(CMSException):
    """
    Lançada quando há erro ao processar idiomas.

    Exemplos:
    - Idioma não é suportado
    - Post não tem conteúdo no idioma solicitado
    - Código de idioma inválido
    """
    pass


class PostError(CMSException):
    """
    Lançada quando há erro ao processar posts.

    Exemplos:
    - Post incompleto (falta título ou conteúdo)
    - Data de publicação inválida
    - Erro ao traduzir post
    """
    pass


class RepositoryError(CMSException):
    """
    Lançada quando há erro ao acessar repositórios.

    Exemplos:
    - Erro ao salvar entidade no repositório
    - Erro ao recuperar dados corrompidos
    - Falha em operação de persistência
    """
    pass


class InvalidInputError(CMSException):
    """
    Lançada quando entrada do usuário é inválida ou fora do intervalo esperado.

    Exemplos:
    - Usuário digita texto quando número é esperado
    - Número de opção fora do intervalo válido
    - Data em formato incorreto
    """
    pass


class OperationFailedError(CMSException):
    """
    Lançada quando uma operação complexa falha por razão desconhecida.

    Exemplos:
    - Falha ao criar post com todos os componentes
    - Falha ao notificar usuário
    - Falha ao processar adapters de notificação
    """
    pass
