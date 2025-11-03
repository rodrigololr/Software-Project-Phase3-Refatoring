from datetime import datetime
from enum import Enum
from typing import Type, TypeVar
import re

from cms.models import MediaType
from cms.exceptions import InvalidInputError, MediaError, ValidationError, InvalidNameError


def validate_name(name: str, field_name: str = "Nome") -> str:
    """
    valida um campo de nome (primeiro nome, último nome, etc).
    
    regras:
    - Não pode estar vazio
    - Apenas letras e espaços permitidos
    - Mínimo 2 caracteres
    - Sem números ou caracteres especiais
    
    raises:
        ValidationError: Se nome é inválido
    
    returns:
        str: Nome validado e trimado
    """
    if not name or not name.strip():
        raise ValidationError(f"{field_name} não pode estar vazio.")
    
    name = name.strip()
    
    # Verifica comprimento mínimo
    if len(name) < 2:
        raise ValidationError(f"{field_name} deve ter no mínimo 2 caracteres.")
    
    # Verifica comprimento máximo
    if len(name) > 50:
        raise ValidationError(f"{field_name} não pode ter mais de 50 caracteres.")
    
    # Permite apenas letras (maiúsculas, minúsculas, acentuadas) e espaços
    if not re.match(r"^[a-záàâãéèêíïóôõöúçñA-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ\s]+$", name):
        raise ValidationError(
            f"{field_name} pode conter apenas letras e espaços. "
            f"Números e caracteres especiais não são permitidos."
        )
    
    return name


def validate_email(email: str) -> str:
    """
    vlida um endereço de email.
    
    raises:
        ValidationError: Se email é inválido
    
    returns:
        str: Email validado
    """
    if not email or not email.strip():
        raise ValidationError("Email não pode estar vazio.")
    
    email = email.strip().lower()
    
    # Padrão simples de email
    if not re.match(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", email):
        raise ValidationError(f"Email '{email}' é inválido.")
    
    return email


def validate_username(username: str) -> str:
    """
    valida um username.
    
    regras:
    - Não pode estar vazio
    - Apenas letras (sem números ou símbolos)
    - Mínimo 3 caracteres
    - Máximo 20 caracteres
    
    raises:
        ValidationError: Se username é inválido

    returns:
        str: Username validado
    """
    if not username or not username.strip():
        raise ValidationError("Username não pode estar vazio.")
    
    username = username.strip()
    
    if len(username) < 3:
        raise ValidationError("Username deve ter no mínimo 3 caracteres.")

    if len(username) > 20:
        raise ValidationError("Username não pode ter mais de 20 caracteres.")

    # Apenas letras permitidas (sem números, underscore ou espaços)
    if not re.match(r"^[a-záàâãéèêíïóôõöúçñA-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ]+$", username):
        # Lança uma exceção mais específica para nome/username inválido
        raise InvalidNameError(
            "Username pode conter apenas letras (sem números ou símbolos)."
        )
    
    return username


def validate_password(password: str) -> str:
    """
    valida uma senha.
    
    regras:
    - Não pode estar vazia
    - Mínimo 6 caracteres
    - Deve conter pelo menos 1 número e 1 letra

    raises:
        ValidationError: Se senha é inválida

    returns:
        str: Senha validada
    """
    if not password or not password.strip():
        raise ValidationError("Senha não pode estar vazia.")
    
    password = password.strip()
    
    if len(password) < 6:
        raise ValidationError("Senha deve ter no mínimo 6 caracteres.")
    
    if not re.search(r"[a-zA-Z]", password):
        raise ValidationError("Senha deve conter pelo menos 1 letra.")
    
    if not re.search(r"[0-9]", password):
        raise ValidationError("Senha deve conter pelo menos 1 número.")
    
    return password


def read_datetime_from_cli() -> datetime:
    """
    lê data e hora do usuário com validação.
    
    raises:
        InvalidInputError: Se formato de data/hora é inválido
    """
    while True:
        try:
            date_str = input(
                "Digite a data que o post deve estar disponível (YYYY-MM-DD): "
            )
            time_str = input("Digite a hora que o post deve estar disponível (HH:MM): ")

            if not date_str.strip() or not time_str.strip():
                raise InvalidInputError("Data e hora não podem estar vazias.")

            combined_str = f"{date_str} {time_str}"
            scheduled_datetime = datetime.strptime(combined_str, "%Y-%m-%d %H:%M")
            return scheduled_datetime
            
        except ValueError:
            print("Formato de data ou hora inválido. Tente novamente (YYYY-MM-DD HH:MM).\n")
        except InvalidInputError as e:
            print(f"{e}\n")


def infer_media_type(extension: str) -> MediaType:
    """
    Infere o tipo de mídia a partir da extensão do arquivo.
    
    Raises:
        ValidationError: Se extension é vazia
        MediaError: Se tipo de arquivo não é suportado
    """
    try:
        if not extension or not extension.strip():
            raise ValidationError("Extensão de arquivo não pode estar vazia.")
        
        ext = extension.lower()
        if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            return MediaType.IMAGE
        elif ext in [".mp4", ".mov", ".avi"]:
            return MediaType.VIDEO
        else:
            raise MediaError(f"Tipo de arquivo '{ext}' não é suportado.")
            
    except (ValidationError, MediaError):
        raise
    except Exception as e:
        raise MediaError(f"Erro ao inferir tipo de mídia: {str(e)}")


E = TypeVar("E", bound=Enum)


def select_enum(enum_cls: Type[E], prompt: str = "Escolha uma opção:") -> E | None:
    """
    Permite o usuário selecionar um valor de um enum com validação.
    
    Raises:
        InvalidInputError: Se opção é inválida
    """
    try:
        print(prompt)
        for i, option in enumerate(enum_cls):
            print(f"{i + 1}. {option.value}")
        print("0. Voltar")
        print(" ")

        while True:
            try:
                selected_option = int(input("Digite a opção desejada: "))
            except ValueError:
                print("Opção inválida. Digite um número.\n")
                continue

            if selected_option == 0:
                return None

            if selected_option < 0 or selected_option > len(enum_cls):
                print("Opção fora do intervalo. Tente novamente.\n")
                continue

            return list(enum_cls)[selected_option - 1]
            
    except Exception as e:
        print(f"Erro ao selecionar opção: {str(e)}")
        return None
    finally:
        print()  # Linha em branco para melhor formatação
