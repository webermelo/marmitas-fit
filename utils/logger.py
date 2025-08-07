# -*- coding: utf-8 -*-
"""
Sistema de Logging para Marmitas Fit
Registra erros, debug e operações do sistema
"""

import streamlit as st
import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path
import json
import os

class MarmitasLogger:
    def __init__(self, name="marmitas_fit"):
        self.name = name
        self.setup_logger()
        self.log_file = self.get_log_file_path()
    
    def setup_logger(self):
        """Configura o logger principal"""
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # Evitar handlers duplicados
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        
        # Formato das mensagens
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para console (desenvolvimento)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Handler para arquivo (se possível)
        try:
            log_file = self.get_log_file_path()
            if log_file:
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Não foi possível criar arquivo de log: {e}")
    
    def get_log_file_path(self):
        """Obtém caminho para arquivo de log"""
        try:
            # Tentar usar diretório atual primeiro
            current_dir = Path.cwd()
            log_dir = current_dir / "logs"
            
            # Criar diretório se não existe
            log_dir.mkdir(exist_ok=True)
            
            # Arquivo de log com data
            log_file = log_dir / f"marmitas_fit_{datetime.now().strftime('%Y%m%d')}.log"
            
            # Testar escrita
            log_file.touch(exist_ok=True)
            
            return str(log_file)
            
        except Exception as e:
            try:
                # Fallback para /tmp em sistemas Unix
                import tempfile
                temp_dir = Path(tempfile.gettempdir())
                log_file = temp_dir / f"marmitas_fit_{datetime.now().strftime('%Y%m%d')}.log"
                log_file.touch(exist_ok=True)
                return str(log_file)
            except:
                # Se tudo falhar, retornar None
                return None
    
    def info(self, message, extra_data=None):
        """Log de informação"""
        self.logger.info(self._format_message(message, extra_data))
    
    def warning(self, message, extra_data=None):
        """Log de aviso"""
        self.logger.warning(self._format_message(message, extra_data))
    
    def error(self, message, exception=None, extra_data=None):
        """Log de erro"""
        error_msg = self._format_message(message, extra_data)
        
        if exception:
            error_msg += f"\nException: {str(exception)}"
            error_msg += f"\nTraceback: {traceback.format_exc()}"
        
        self.logger.error(error_msg)
        
        # Também exibir no Streamlit se disponível
        try:
            if st.session_state:  # Verifica se Streamlit está ativo
                st.error(f"🔥 Erro registrado: {message}")
                if st.checkbox("Mostrar detalhes técnicos"):
                    st.code(error_msg)
        except:
            pass
    
    def debug(self, message, extra_data=None):
        """Log de debug"""
        self.logger.debug(self._format_message(message, extra_data))
    
    def log_user_action(self, action, user_email=None, details=None):
        """Log de ação do usuário"""
        user = user_email or "anônimo"
        message = f"AÇÃO: {action} por {user}"
        self.info(message, details)
    
    def log_system_start(self):
        """Log de início do sistema"""
        self.info("=== SISTEMA INICIADO ===", {
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "working_directory": str(Path.cwd())
        })
    
    def log_page_access(self, page_name, user_email=None):
        """Log de acesso a página"""
        self.log_user_action(f"Acessou página {page_name}", user_email)
    
    def log_import_error(self, module_name, error):
        """Log específico para erros de importação"""
        self.error(f"Erro ao importar módulo: {module_name}", error, {
            "module": module_name,
            "error_type": type(error).__name__
        })
    
    def _format_message(self, message, extra_data=None):
        """Formata mensagem com dados extras"""
        formatted = str(message)
        
        if extra_data:
            try:
                extra_str = json.dumps(extra_data, indent=2, ensure_ascii=False, default=str)
                formatted += f"\nDados extras: {extra_str}"
            except:
                formatted += f"\nDados extras: {str(extra_data)}"
        
        return formatted
    
    def get_recent_logs(self, lines=50):
        """Obtém logs recentes para exibição"""
        try:
            if self.log_file and Path(self.log_file).exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()
                    return ''.join(all_lines[-lines:])
            return "Arquivo de log não encontrado"
        except Exception as e:
            return f"Erro ao ler logs: {e}"

# Instância global do logger
logger = MarmitasLogger()

def log_exception(func):
    """Decorator para capturar exceções automaticamente"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            func_name = f"{func.__module__}.{func.__name__}"
            logger.error(f"Erro na função {func_name}", e, {
                "function": func_name,
                "args": str(args),
                "kwargs": str(kwargs)
            })
            raise
    return wrapper

def safe_import(module_name, fallback=None):
    """Importação segura com logging"""
    try:
        module = __import__(module_name)
        logger.debug(f"Módulo importado com sucesso: {module_name}")
        return module
    except Exception as e:
        logger.log_import_error(module_name, e)
        if fallback:
            logger.warning(f"Usando fallback para {module_name}: {fallback}")
            return fallback
        return None

def init_logging():
    """Inicializar sistema de logging"""
    logger.log_system_start()
    return logger

# Auto-inicialização
if __name__ != "__main__":
    init_logging()