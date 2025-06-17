#!/usr/bin/env python3
"""
Script para criar usuário de teste para upload de currículo
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def create_test_user():
    """Cria usuário de teste"""
    app = create_app()
    
    with app.app_context():
        # Verificar se usuário já existe
        existing_user = User.query.filter_by(email='test@jobmate.com').first()
        if existing_user:
            print("✅ Usuário de teste já existe:")
            print(f"   📧 Email: {existing_user.email}")
            print(f"   👤 Nome: {existing_user.first_name} {existing_user.last_name}")
            print(f"   🎯 Tipo: {'Candidato' if existing_user.user_type == 'applicant' else 'Recrutador'}")
            return existing_user
        
        # Criar novo usuário
        test_user = User.create_user(
            email='test@jobmate.com',
            password='123456',
            first_name='João',
            last_name='Silva',
            user_type='applicant',
            is_verified=True,
            is_active=True
        )
        
        print("✅ Usuário de teste criado com sucesso!")
        print(f"   📧 Email: {test_user.email}")
        print(f"   🔑 Senha: 123456")
        print(f"   👤 Nome: {test_user.first_name} {test_user.last_name}")
        print(f"   🎯 Tipo: Candidato")
        
        return test_user

if __name__ == "__main__":
    try:
        user = create_test_user()
        print("\n🚀 Agora você pode fazer login em http://localhost:5002/auth/login")
        print("   e testar o upload em http://localhost:5002/resume/upload")
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1) 