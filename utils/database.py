# -*- coding: utf-8 -*-
"""
Operações de banco de dados - Firestore UNIFICADO
VERSÃO CORRIGIDA: Usa FirestoreClient + TokenManager para resolver problemas de persistência
"""

import streamlit as st
import pandas as pd
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        # CORREÇÃO CRÍTICA: Usar FirestoreClient com TokenManager em vez de firebase_admin
        self.db = None
        self._init_firestore_client()
    
    def _init_firestore_client(self):
        """Inicializa cliente Firestore usando o sistema unificado"""
        try:
            from .firestore_client import get_firestore_client
            self.db = get_firestore_client()
            if self.db:
                st.success("🔥 DatabaseManager: Cliente Firestore inicializado com sucesso")
            else:
                st.warning("⚠️ DatabaseManager: Cliente Firestore não disponível - usando modo demo")
        except Exception as e:
            st.error(f"❌ Erro ao inicializar Firestore: {e}")
            self.db = None
    
    def get_user_data_path(self, user_id, collection_type="ingredients"):
        """Gera path da coleção específica do usuário (CORRIGIDO para usar padrão unificado)"""
        return f"users/{user_id}/{collection_type}"
    
    # ==================== INGREDIENTES ====================
    
    def save_ingredient(self, user_id, ingredient_data):
        """Salva um ingrediente no Firestore (VERSÃO CORRIGIDA)"""
        try:
            if not self.db:
                st.error("❌ Banco de dados não disponível")
                return False
            
            # CORREÇÃO: Usar caminho unificado
            collection_path = self.get_user_data_path(user_id, "ingredients")
            
            # CORREÇÃO: Converter estrutura App → Firebase antes de salvar
            firebase_data = self._convert_app_to_firebase_structure(ingredient_data)
            firebase_data.update({
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })
            
            st.info(f"📍 Salvando ingrediente em: {collection_path}")
            
            # CORREÇÃO: Usar método .add() do FirestoreClient customizado
            result = self.db.collection(collection_path).add(firebase_data)
            
            if result:
                st.success(f"✅ Ingrediente '{ingredient_data.get('Nome', 'N/A')}' salvo com sucesso!")
                return True
            else:
                st.error("❌ Falha ao salvar no Firebase")
                return False
            
        except Exception as e:
            st.error(f"❌ Erro ao salvar ingrediente: {e}")
            import traceback
            st.code(traceback.format_exc())
            return False
    
    def get_user_ingredients(self, user_id):
        """Busca ingredientes do usuário (VERSÃO CORRIGIDA)"""
        try:
            if not self.db:
                st.warning("⚠️ Firebase não disponível - retornando ingredientes demo")
                return self.get_demo_ingredients()
            
            # CORREÇÃO: Usar caminho unificado users/{user_id}/ingredients
            collection_path = self.get_user_data_path(user_id, "ingredients")
            st.info(f"📍 Carregando ingredientes de: {collection_path}")
            
            # CORREÇÃO: Usar método .get() do FirestoreClient customizado
            docs = self.db.collection(collection_path).get()
            
            st.info(f"🔍 Encontrados {len(docs) if docs else 0} documentos")
            
            if not docs:
                st.warning(f"⚠️ Nenhum ingrediente encontrado em: {collection_path}")
                return pd.DataFrame()
            
            ingredients = []
            for doc in docs:
                # Converter estrutura Firebase → App
                converted = self._convert_firebase_to_app_structure(doc)
                if converted:
                    ingredients.append(converted)
            
            st.success(f"✅ {len(ingredients)} ingredientes carregados e convertidos")
            return pd.DataFrame(ingredients) if ingredients else pd.DataFrame()
            
        except Exception as e:
            st.error(f"❌ Erro ao carregar ingredientes: {e}")
            import traceback
            st.code(traceback.format_exc())
            return self.get_demo_ingredients()
    
    def update_ingredient(self, user_id, ingredient_id, ingredient_data):
        """Atualiza um ingrediente (VERSÃO CORRIGIDA)"""
        try:
            if not self.db:
                return False
            
            # CORREÇÃO: Usar caminho unificado
            collection_path = self.get_user_data_path(user_id, "ingredients")
            
            # Converter e adicionar timestamp
            firebase_data = self._convert_app_to_firebase_structure(ingredient_data)
            firebase_data["updated_at"] = datetime.now().isoformat()
            
            result = self.db.collection(collection_path).document(ingredient_id).set(firebase_data)
            return result is not None
            
        except Exception as e:
            st.error(f"❌ Erro ao atualizar ingrediente: {e}")
            return False
    
    def delete_ingredient(self, user_id, ingredient_id):
        """Deleta um ingrediente (VERSÃO CORRIGIDA)"""
        try:
            if not self.db:
                return False
            
            # CORREÇÃO: Usar caminho unificado
            collection_path = self.get_user_data_path(user_id, "ingredients")
            
            # Usar método de deleção do FirestoreClient (se implementado)
            # Por enquanto, retornar False pois delete não está implementado
            st.warning("⚠️ Função de exclusão ainda não implementada")
            return False
            
        except Exception as e:
            st.error(f"❌ Erro ao deletar ingrediente: {e}")
            return False
    
    # ==================== RECEITAS ====================
    
    def save_recipe(self, user_id, recipe_data):
        """Salva uma receita no Firestore (VERSÃO CORRIGIDA)"""
        try:
            if not self.db:
                # Modo demo - salvar na sessão
                if 'demo_recipes' not in st.session_state:
                    st.session_state.demo_recipes = []
                
                recipe_data.update({
                    "user_id": user_id,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "id": f"demo_recipe_{len(st.session_state.demo_recipes)}"
                })
                
                st.session_state.demo_recipes.append(recipe_data)
                st.info(f"🍽️ Receita salva no modo demo: {recipe_data.get('nome_receita', 'N/A')}")
                return True
            
            # CORREÇÃO: Usar caminho unificado para receitas
            collection_path = self.get_user_data_path(user_id, "recipes")
            
            recipe_data.update({
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })
            
            result = self.db.collection(collection_path).add(recipe_data)
            
            if result:
                st.success(f"✅ Receita '{recipe_data.get('nome_receita', 'N/A')}' salva no Firebase!")
                return True
            else:
                st.error("❌ Falha ao salvar receita no Firebase")
                return False
            
        except Exception as e:
            st.error(f"❌ Erro ao salvar receita: {e}")
            return False
    
    def get_user_recipes(self, user_id):
        """Busca receitas do usuário (VERSÃO CORRIGIDA)"""
        try:
            if not self.db:
                # Modo demo - buscar da sessão
                if 'demo_recipes' not in st.session_state:
                    st.session_state.demo_recipes = []
                
                st.info(f"🍽️ Carregando receitas do demo: {len(st.session_state.demo_recipes)} encontradas")
                return pd.DataFrame(st.session_state.demo_recipes) if st.session_state.demo_recipes else pd.DataFrame()
            
            # CORREÇÃO: Usar caminho unificado
            collection_path = self.get_user_data_path(user_id, "recipes")
            
            docs = self.db.collection(collection_path).get()
            
            st.info(f"🔍 Encontradas {len(docs) if docs else 0} receitas")
            
            if not docs:
                return pd.DataFrame()
            
            recipes = []
            for doc in docs:
                doc['id'] = doc.get('id', '')  # Garantir que tem ID
                recipes.append(doc)
            
            return pd.DataFrame(recipes) if recipes else pd.DataFrame()
            
        except Exception as e:
            st.error(f"❌ Erro ao carregar receitas: {e}")
            return pd.DataFrame()
    
    def update_recipe(self, recipe_id, recipe_data):
        """Atualiza uma receita"""
        try:
            if not self.db:
                return False
            
            recipe_data["updated_at"] = datetime.now()
            self.db.collection(COLLECTIONS["recipes"]).document(recipe_id).update(recipe_data)
            return True
            
        except Exception as e:
            st.error(f"Erro ao atualizar receita: {e}")
            return False
    
    def delete_recipe(self, recipe_id):
        """Deleta uma receita"""
        try:
            if not self.db:
                return False
            
            self.db.collection(COLLECTIONS["recipes"]).document(recipe_id).delete()
            return True
            
        except Exception as e:
            st.error(f"Erro ao deletar receita: {e}")
            return False
    
    # ==================== DADOS DEMO ====================
    
    def _convert_firebase_to_app_structure(self, firebase_doc):
        """Converte documento Firebase para estrutura esperada pela app"""
        try:
            # Estrutura Firebase (salva pelo admin) → Estrutura App
            converted = {
                'Nome': firebase_doc.get('nome', ''),
                'Categoria': firebase_doc.get('categoria', ''),
                'Unidade_Receita': firebase_doc.get('unid_receita', 'g'),
                'Unidade_Compra': firebase_doc.get('unid_compra', 'kg'),
                'Preco_Padrao': float(firebase_doc.get('preco', 0.0)),
                'Kcal_Por_Unidade_Receita': float(firebase_doc.get('kcal_unid', 0.0)),
                'Fator_Conversao': float(firebase_doc.get('fator_conv', 1.0)),
                'Ativo': firebase_doc.get('ativo', True),
                'Observacoes': firebase_doc.get('observacoes', ''),
                'id': firebase_doc.get('id', '')
            }
            return converted
        except Exception as e:
            st.error(f"❌ Erro ao converter estrutura Firebase: {e}")
            return None
    
    def _convert_app_to_firebase_structure(self, app_data):
        """Converte estrutura da app para estrutura Firebase"""
        try:
            # Estrutura App → Estrutura Firebase
            converted = {
                'nome': app_data.get('Nome', ''),
                'categoria': app_data.get('Categoria', ''),
                'unid_receita': app_data.get('Unidade_Receita', 'g'),
                'unid_compra': app_data.get('Unidade_Compra', 'kg'),
                'preco': float(app_data.get('Preco_Padrao', 0.0)),
                'kcal_unid': float(app_data.get('Kcal_Por_Unidade_Receita', 0.0)),
                'fator_conv': float(app_data.get('Fator_Conversao', 1.0)),
                'ativo': app_data.get('Ativo', True),
                'observacoes': app_data.get('Observacoes', '')
            }
            return converted
        except Exception as e:
            st.error(f"❌ Erro ao converter estrutura App: {e}")
            return app_data  # Retornar original se conversão falhar
    
    def get_demo_ingredients(self):
        """Retorna ingredientes de demonstração"""
        demo_data = {
            'Nome': [
                'Frango (peito)', 'Frango (coxa/sobrecoxa)', 'Carne bovina (patinho)', 
                'Arroz integral', 'Batata doce', 'Brócolis', 'Tomate', 'Cenoura',
                'Feijão preto', 'Lentilha', 'Azeite de oliva', 'Sal'
            ],
            'Categoria': [
                'Proteína Animal', 'Proteína Animal', 'Proteína Animal',
                'Carboidrato', 'Carboidrato', 'Vegetal', 'Vegetal', 'Vegetal', 
                'Leguminosa', 'Leguminosa', 'Gordura', 'Tempero'
            ],
            'Unidade_Receita': ['g'] * 12,
            'Unidade_Compra': ['kg'] * 12,
            'Preco_Padrao': [18.9, 12.9, 42.9, 8.9, 4.5, 8.9, 5.9, 3.9, 9.9, 12.9, 35.0, 3.0],
            'Kcal_Por_Unidade_Receita': [1.65, 2.21, 2.19, 1.11, 0.86, 0.34, 0.18, 0.41, 0.77, 1.16, 8.84, 0],
            'Fator_Conversao': [1000] * 12
        }
        return pd.DataFrame(demo_data)
    
    def init_user_data(self, user_id):
        """Inicializa dados do usuário com ingredientes padrão"""
        try:
            # Verificar se usuário já tem ingredientes
            existing = self.get_user_ingredients(user_id)
            if len(existing) > 0:
                return True
            
            # Criar ingredientes padrão
            demo_ingredients = self.get_demo_ingredients()
            
            for _, ingredient in demo_ingredients.iterrows():
                ingredient_data = ingredient.to_dict()
                self.save_ingredient(user_id, ingredient_data)
            
            return True
            
        except Exception as e:
            st.error(f"Erro ao inicializar dados do usuário: {e}")
            return False

# Instância global do Database Manager
def get_database_manager():
    if 'database_manager' not in st.session_state:
        st.session_state.database_manager = DatabaseManager()
    return st.session_state.database_manager