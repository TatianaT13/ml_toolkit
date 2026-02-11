import streamlit as st
import pandas as pd
from my_ml_toolkit.pipeline import MLPipeline

st.set_page_config(page_title="ML Toolkit - Malware Detection", page_icon="🛡️")

st.title("🛡️ ML Toolkit - Malware Detection")
st.markdown("Détectez les malwares avec du Machine Learning")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    data_type = st.selectbox("Type de données", ["tabular", "binary", "text"])
    task_type = st.selectbox("Type de tâche", ["classification", "regression"])
    
    st.markdown("---")
    st.markdown("### 📊 À propos")
    st.info("Cet outil utilise 5 modèles ML pour détecter les malwares")

# Main content
tab1, tab2, tab3 = st.tabs(["📤 Upload & Train", "🔍 Prédiction", "📈 Résultats"])

with tab1:
    st.header("Entraîner un modèle")
    
    uploaded_file = st.file_uploader("Choisissez un fichier CSV", type=['csv'])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ Fichier chargé: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        st.dataframe(df.head())
        
        target_col = st.selectbox("Colonne cible", df.columns)
        
        if st.button("🚀 Lancer l'entraînement", type="primary"):
            with st.spinner("Entraînement en cours..."):
                # Sauvegarder temporairement
                temp_path = "/tmp/uploaded_data.csv"
                df.to_csv(temp_path, index=False)
                
                # Créer pipeline
                pipeline = MLPipeline(data_type=data_type, task_type=task_type)
                
                # Entraîner
                results = pipeline.run_full_pipeline(temp_path, target_col=target_col, verbose=False)
                
                if results:
                    st.session_state['results'] = results
                    st.session_state['pipeline'] = pipeline
                    st.success("✅ Entraînement terminé!")
                    
                    # Afficher résultats
                    st.subheader("📊 Performances des modèles")
                    results_df = pd.DataFrame(results).T
                    st.dataframe(results_df.style.highlight_max(axis=0))

with tab2:
    st.header("Faire une prédiction")
    
    if 'pipeline' not in st.session_state:
        st.warning("⚠️ Veuillez d'abord entraîner un modèle dans l'onglet 'Upload & Train'")
    else:
        predict_file = st.file_uploader("Fichier pour prédiction", type=['csv'], key="predict")
        
        if predict_file and st.button("🔮 Prédire"):
            df_pred = pd.read_csv(predict_file)
            
            # Prédiction
            temp_pred_path = "/tmp/predict_data.csv"
            df_pred.to_csv(temp_pred_path, index=False)
            
            predictions = st.session_state['pipeline'].predict_new_data(temp_pred_path)
            
            df_pred['Prédiction'] = predictions
            st.dataframe(df_pred)
            
            # Télécharger résultats
            csv = df_pred.to_csv(index=False)
            st.download_button("💾 Télécharger les résultats", csv, "predictions.csv")

with tab3:
    st.header("Résultats d'entraînement")
    
    if 'results' in st.session_state:
        results = st.session_state['results']
        
        # Meilleur modèle
        best_model = max(results.items(), key=lambda x: x[1]['accuracy'])
        st.success(f"🏆 Meilleur modèle: **{best_model[0]}** ({best_model[1]['accuracy']:.2%})")
        
        # Graphique
        import plotly.express as px
        
        results_df = pd.DataFrame(results).T.reset_index()
        results_df.columns = ['Modèle', 'Accuracy', 'Precision', 'Recall', 'F1']
        
        fig = px.bar(results_df, x='Modèle', y='Accuracy', 
                     title="Comparaison des modèles",
                     color='Accuracy',
                     color_continuous_scale='viridis')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucun résultat disponible. Entraînez d'abord un modèle!")
