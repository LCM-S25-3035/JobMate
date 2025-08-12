"""
Utility functions for JobMate application
"""

# This file makes the utils directory a Python package
import re
from typing import Tuple, Optional


def calculate_profile_completion(user):
    """Calculate profile completion percentage"""
    from flask import current_app
    
    completion_items = []
    total_possible = 0
    completed = 0
    
    # Essential profile fields to check
    profile_checks = [
        ('email', 'Email address', getattr(user, 'email', None)),
        ('first_name', 'First name', getattr(user, 'first_name', None)),
        ('last_name', 'Last name', getattr(user, 'last_name', None)),
        ('phone', 'Phone number', getattr(user, 'phone', None)),
        ('city', 'Location', getattr(user, 'city', None)),
        ('bio', 'Professional summary', getattr(user, 'bio', None)),
        ('skills', 'Skills', getattr(user, 'skills', None)),
        ('experience_level', 'Experience level', getattr(user, 'experience_level', None))
    ]
    
    # Check each field
    for field_name, display_name, field_value in profile_checks:
        total_possible += 1
        
        is_complete = False
        if field_value is not None:
            if isinstance(field_value, str):
                is_complete = field_value.strip() != ''
            elif isinstance(field_value, list):
                is_complete = len(field_value) > 0
            else:
                is_complete = True
        
        completion_items.append({
            'field': field_name,
            'name': display_name,
            'completed': is_complete,
            'value': field_value
        })
        
        if is_complete:
            completed += 1
    
    # Calculate percentage
    completion_percentage = round((completed / total_possible) * 100) if total_possible > 0 else 0
    
    return {
        'percentage': completion_percentage,
        'completed': completed,
        'total': total_possible,
        'items': completion_items,
        'missing_items': [item for item in completion_items if not item['completed']]
    }


def split_answer_and_code(raw_text: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Separa el texto de la 'expected answer' del posible bloque de código.
    Devuelve: (answer_text, code_snippet or None, code_lang or None)

    Lógica:
    1) Busca primero bloques con triple backticks ```lang\ncode\n```
    2) Si no encuentra, busca el marcador "CODE SNIPPET" (con "IF APPLICABLE" opcional)
       y toma todo lo que venga después como código (útil para respuestas que no usan
       fences).
    3) Si no hay snippet, devuelve (raw_text, None, None).
    """
    if not raw_text:
        return "", None, None

    # 1) Buscar triple backticks
    fence_re = re.search(r"```(?:\s*?)(\w+)?\n(.*?)```", raw_text, re.DOTALL | re.IGNORECASE)
    if fence_re:
        lang = (fence_re.group(1) or "plaintext").lower()
        code = fence_re.group(2).strip()
        # Texto sin el bloque de código
        answer = (raw_text[:fence_re.start()] + raw_text[fence_re.end():]).strip()
        return answer, code, lang

    # 2) Buscar marcador "CODE SNIPPET" (IF APPLICABLE) y tomar lo que sigue
    marker_re = re.search(
        r"CODE SNIPPET(?:\s*\(IF APPLICABLE\))?\s*:?\s*(.*)$",
        raw_text,
        re.IGNORECASE | re.DOTALL
    )
    if marker_re:
        code_block = marker_re.group(1).strip()
        answer = raw_text[:marker_re.start()].strip()
        # Intentar detectar language si la primera línea es un nombre de lenguaje (p.e. "Python")
        first_line = (code_block.splitlines()[0].strip() if code_block else "")
        lang_guess = None
        if first_line and re.match(r"^[A-Za-z0-9_+-]+$", first_line) and len(first_line) <= 20:
            # Si la primera línea parece solo "Python" o "python", úsala como lenguaje
            lang_guess = first_line.lower()
            # elimina la primera línea del código (porque era solo la etiqueta del lenguaje)
            code_block = "\n".join(code_block.splitlines()[1:]).strip()

        return answer, (code_block or None), (lang_guess or "python")

    # 3) No hay snippet
    return raw_text.strip(), None, None
