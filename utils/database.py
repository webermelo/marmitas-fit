# -*- coding: utf-8 -*-
"""
Operações de banco de dados - Firestore
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from config.firebase_config import get_firebase_manager, COLLECTIONS

class DatabaseManager:
    def __init__(self):
        self.firebase = get_firebase_manager()
        self.db = self.firebase.get_firestore_client()
    
    def get_user_data_path(self, collection, user_id):
        """Gera path da coleção específica do usuário"""
        return f"{collection}/{user_id}"
    
    # ==================== INGREDIENTES ====================
    
    def save_ingredient(self, user_id, ingredient_data):
        """Salva um ingrediente no Firestore"""
        try:
            if not self.db:
                st.error("Banco de dados não disponível")
                return False
            
            doc_ref = self.db.collection(COLLECTIONS["ingredients"]).document()
            ingredient_data.update({
                "user_id": user_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            doc_ref.set(ingredient_data)
            return True
            
        except Exception as e:
            st.error(f"Erro ao salvar ingrediente: {e}")
            return False
    
    def get_user_ingredients(self, user_id):
        """Busca ingredientes do usuário"""
        try:
            if not self.db:
                return self.get_demo_ingredients()
            
            docs = self.db.collection(COLLECTIONS["ingredients"]).where("user_id", "==", user_id).get()
            ingredients = []
            
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                ingredients.append(data)
            
            return pd.DataFrame(ingredients) if ingredients else pd.DataFrame()
            
        except Exception as e:
            st.error(f"Erro ao carregar ingredientes: {e}")
            return self.get_demo_ingredients()
    
    def update_ingredient(self, ingredient_id, ingredient_data):
        """Atualiza um ingrediente"""
        try:
            if not self.db:
                return False
            
            ingredient_data["updated_at"] = datetime.now()
            self.db.collection(COLLECTIONS["ingredients"]).document(ingredient_id).update(ingredient_data)
            return True
            
        except Exception as e:
            st.error(f"Erro ao atualizar ingrediente: {e}")
            return False
    
    def delete_ingredient(self, ingredient_id):
        """Deleta um ingrediente"""
        try:
            if not self.db:
                return False
            
            self.db.collection(COLLECTIONS["ingredients"]).document(ingredient_id).delete()
            return True
            
        except Exception as e:
            st.error(f"Erro ao deletar ingrediente: {e}")
            return False
    
    # ==================== RECEITAS ====================
    
    def save_recipe(self, user_id, recipe_data):
        """Salva uma receita no Firestore ou sessão (modo demo)"""
        try:
            if not self.db:
                # Modo demo - salvar na sessão
                if 'demo_recipes' not in st.session_state:
                    st.session_state.demo_recipes = []
                
                recipe_data.update({
                    "user_id": user_id,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "id": f"demo_recipe_{len(st.session_state.demo_recipes)}"
                })
                
                st.session_state.demo_recipes.append(recipe_data)
                print(f"DEBUG: Receita salva no modo demo: {recipe_data['nome_receita']}")
                return True
            
            # Modo Firebase
            doc_ref = self.db.collection(COLLECTIONS["recipes"]).document()
            recipe_data.update({
                "user_id": user_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            doc_ref.set(recipe_data)
            return True
            
        except Exception as e:
            st.error(f"Erro ao salvar receita: {e}")
            return False
    
    def get_user_recipes(self, user_id):
        """Busca receitas do usuário"""
        try:
            if not self.db:
                # Modo demo - buscar da sessão
                if 'demo_recipes' not in st.session_state:
                    st.session_state.demo_recipes = []
                
                print(f"DEBUG: Carregando receitas do demo: {len(st.session_state.demo_recipes)} encontradas")
                return pd.DataFrame(st.session_state.demo_recipes) if st.session_state.demo_recipes else pd.DataFrame()
            
            # Modo Firebase
            docs = self.db.collection(COLLECTIONS["recipes"]).where("user_id", "==", user_id).get()
            recipes = []
            
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                recipes.append(data)
            
            return pd.DataFrame(recipes) if recipes else pd.DataFrame()
            
        except Exception as e:
            st.error(f"Erro ao carregar receitas: {e}")
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