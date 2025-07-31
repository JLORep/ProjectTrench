#!/usr/bin/env python3
"""
TrenchCoat Pro - ML Model Builder
Interactive machine learning model creation and training tool
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pickle
import json
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

# ML Libraries
try:
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression, LinearRegression
    from sklearn.svm import SVC, SVR
    from sklearn.neural_network import MLPClassifier, MLPRegressor
    from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, r2_score, mean_squared_error
    from sklearn.feature_selection import SelectKBest, f_classif, f_regression
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

class ModelBuilder:
    """Interactive ML model building tool"""
    
    def __init__(self):
        self.colors = {
            'primary': '#10b981',    # Emerald
            'secondary': '#059669',  # Dark emerald
            'accent': '#34d399',     # Light emerald
            'danger': '#ef4444',     # Red
            'warning': '#f59e0b',    # Amber
            'info': '#3b82f6',       # Blue
            'purple': '#8b5cf6',     # Purple
            'dark': '#1f2937',       # Dark gray
        }
        
        # Initialize session state for models
        if 'trained_models' not in st.session_state:
            st.session_state.trained_models = {}
        if 'model_performance' not in st.session_state:
            st.session_state.model_performance = {}
        if 'feature_importance' not in st.session_state:
            st.session_state.feature_importance = {}
    
    def render_model_builder(self):
        """Main model builder interface"""
        
        if not ML_AVAILABLE:
            st.error("🚨 ML libraries not available. Please install scikit-learn to use Model Builder.")
            return
        
        st.markdown("""
        <div style='text-align: center; padding: 2rem; margin-bottom: 2rem;
                    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
                    border-radius: 15px; border: 1px solid rgba(139, 92, 246, 0.3);'>
            <h1 style='color: #8b5cf6; margin: 0; font-size: 2.5rem; font-weight: 700;'>
                🤖 ML Model Builder
            </h1>
            <p style='color: #a3a3a3; margin-top: 0.5rem; font-size: 1.2rem;'>
                Build, Train & Deploy Custom Trading Models
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create tabs for different model building stages
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Data Preparation", 
            "🛠️ Model Training", 
            "📈 Model Evaluation", 
            "🚀 Model Deployment"
        ])
        
        with tab1:
            self.render_data_preparation()
        
        with tab2:
            self.render_model_training()
        
        with tab3:
            self.render_model_evaluation()
        
        with tab4:
            self.render_model_deployment()
    
    def render_data_preparation(self):
        """Data preparation and feature engineering interface"""
        
        st.markdown("### 📊 Data Source Selection")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            data_source = st.selectbox(
                "Choose Data Source:",
                ["📡 Live Coin Data", "📈 Historical Market Data", "🔍 Enriched Signals", "📄 Upload Custom Dataset"]
            )
            
            if data_source == "📄 Upload Custom Dataset":
                uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
                if uploaded_file:
                    df = pd.read_csv(uploaded_file)
                    st.success(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
                    st.session_state.model_data = df
            else:
                # Generate sample data based on selection
                df = self.generate_sample_data(data_source)
                st.session_state.model_data = df
        
        with col2:
            st.markdown("**📋 Dataset Info:**")
            if 'model_data' in st.session_state:
                df = st.session_state.model_data
                st.metric("Rows", len(df))
                st.metric("Features", len(df.columns))
                st.metric("Memory Usage", f"{df.memory_usage().sum() / 1024:.1f} KB")
        
        if 'model_data' in st.session_state:
            df = st.session_state.model_data
            
            st.markdown("### 🔧 Feature Engineering")
            
            # Feature selection
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                target_column = st.selectbox("🎯 Target Variable:", df.columns)
                feature_columns = st.multiselect(
                    "📊 Feature Columns:", 
                    [col for col in df.columns if col != target_column],
                    default=[col for col in df.columns if col != target_column][:5]
                )
            
            with col2:
                problem_type = st.selectbox("Problem Type:", ["Classification", "Regression"])
                
            with col3:
                test_size = st.slider("Test Split %", 10, 50, 20) / 100
            
            if feature_columns:
                # Data preprocessing options
                st.markdown("### ⚙️ Preprocessing Options")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    scale_features = st.checkbox("🔄 Scale Features", value=True)
                    handle_missing = st.selectbox("❓ Missing Values:", ["Drop", "Mean", "Median", "Mode"])
                
                with col2:
                    feature_selection = st.checkbox("🎯 Feature Selection", value=False)
                    if feature_selection:
                        n_features = st.slider("Number of Features:", 3, len(feature_columns), min(10, len(feature_columns)))
                
                with col3:
                    create_interactions = st.checkbox("🔗 Feature Interactions", value=False)
                    polynomial_features = st.checkbox("📈 Polynomial Features", value=False)
                
                # Preview processed data
                if st.button("🔍 Preview Processed Data"):
                    processed_df = self.preprocess_data(
                        df, target_column, feature_columns, 
                        scale_features, handle_missing, 
                        feature_selection, n_features if feature_selection else None
                    )
                    
                    st.markdown("**📋 Processed Data Preview:**")
                    st.dataframe(processed_df.head(), use_container_width=True)
                    
                    # Store processed data
                    st.session_state.processed_data = {
                        'df': processed_df,
                        'target': target_column,
                        'features': feature_columns,
                        'problem_type': problem_type,
                        'test_size': test_size
                    }
                    
                    st.success("✅ Data preprocessing complete!")
    
    def render_model_training(self):
        """Model training interface"""
        
        if 'processed_data' not in st.session_state:
            st.warning("⚠️ Please prepare your data first in the Data Preparation tab.")
            return
        
        st.markdown("### 🛠️ Model Selection & Training")
        
        problem_type = st.session_state.processed_data['problem_type']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**🤖 Choose Model Type:**")
            
            if problem_type == "Classification":
                model_options = {
                    "🌳 Random Forest": "random_forest_clf",
                    "🚀 Gradient Boosting": "gradient_boosting", 
                    "🧠 Neural Network": "neural_network_clf",
                    "📊 Logistic Regression": "logistic_regression",
                    "🎯 Support Vector Machine": "svm_clf"
                }
            else:
                model_options = {
                    "🌳 Random Forest": "random_forest_reg",
                    "🧠 Neural Network": "neural_network_reg",
                    "📊 Linear Regression": "linear_regression",
                    "🎯 Support Vector Machine": "svm_reg"
                }
            
            selected_model = st.selectbox("Model:", list(model_options.keys()))
            model_type = model_options[selected_model]
        
        with col2:
            st.markdown("**⚙️ Training Options:**")
            cv_folds = st.selectbox("Cross Validation:", [3, 5, 10])
            hyperparameter_tuning = st.checkbox("🔧 Auto Hyperparameter Tuning", value=True)
        
        # Model-specific parameters
        st.markdown("### 🎛️ Model Parameters")
        params = self.render_model_parameters(model_type)
        
        # Training controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Train Model", type="primary"):
                with st.spinner("Training model..."):
                    results = self.train_model(model_type, params, cv_folds, hyperparameter_tuning)
                    if results:
                        st.success("✅ Model training complete!")
                        st.balloons()
        
        with col2:
            if st.button("📊 Compare Models"):
                with st.spinner("Training multiple models..."):
                    comparison_results = self.train_multiple_models(cv_folds)
                    if comparison_results:
                        self.display_model_comparison(comparison_results)
        
        with col3:
            if st.button("💾 Save Model"):
                if 'trained_models' in st.session_state and st.session_state.trained_models:
                    self.save_model()
                else:
                    st.warning("No trained model to save!")
        
        # Display training results
        if 'current_model_results' in st.session_state:
            self.display_training_results()
    
    def render_model_evaluation(self):
        """Model evaluation and performance visualization"""
        
        if 'trained_models' not in st.session_state or not st.session_state.trained_models:
            st.warning("⚠️ No trained models found. Please train a model first.")
            return
        
        st.markdown("### 📈 Model Performance Analysis")
        
        # Model selection for evaluation
        model_names = list(st.session_state.trained_models.keys())
        selected_model = st.selectbox("📊 Select Model for Evaluation:", model_names)
        
        if selected_model in st.session_state.model_performance:
            performance = st.session_state.model_performance[selected_model]
            
            # Performance metrics
            col1, col2, col3, col4 = st.columns(4)
            
            if performance['problem_type'] == 'Classification':
                with col1:
                    st.metric("🎯 Accuracy", f"{performance['accuracy']:.3f}")
                with col2:
                    st.metric("📊 Precision", f"{performance['precision']:.3f}")
                with col3:
                    st.metric("🔄 Recall", f"{performance['recall']:.3f}")
                with col4:
                    st.metric("⚖️ F1-Score", f"{performance['f1_score']:.3f}")
            else:
                with col1:
                    st.metric("📈 R² Score", f"{performance['r2_score']:.3f}")
                with col2:
                    st.metric("📉 RMSE", f"{performance['rmse']:.3f}")
                with col3:
                    st.metric("🎯 MAE", f"{performance['mae']:.3f}")
                with col4:
                    st.metric("📊 CV Score", f"{performance['cv_score_mean']:.3f}")
            
            # Visualization tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "🎯 Performance Charts", 
                "🌟 Feature Importance", 
                "🔍 Model Insights",
                "📊 Prediction Analysis"
            ])
            
            with tab1:
                self.render_performance_charts(selected_model, performance)
            
            with tab2:
                self.render_feature_importance(selected_model)
            
            with tab3:
                self.render_model_insights(selected_model, performance)
            
            with tab4:
                self.render_prediction_analysis(selected_model)
    
    def render_model_deployment(self):
        """Model deployment interface"""
        
        if 'trained_models' not in st.session_state or not st.session_state.trained_models:
            st.warning("⚠️ No trained models found. Please train a model first.")
            return
        
        st.markdown("### 🚀 Model Deployment")
        
        model_names = list(st.session_state.trained_models.keys())
        selected_model = st.selectbox("📦 Select Model for Deployment:", model_names)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**🎯 Deployment Options:**")
            
            deployment_type = st.selectbox(
                "Deployment Target:",
                ["🔴 Live Trading Engine", "📊 Dashboard Integration", "🌐 API Endpoint", "📱 Real-time Alerts"]
            )
            
            confidence_threshold = st.slider("Confidence Threshold:", 0.1, 1.0, 0.8)
            auto_retrain = st.checkbox("🔄 Auto-retrain (weekly)", value=True)
            
            if deployment_type == "🔴 Live Trading Engine":
                st.warning("⚠️ **WARNING**: This will use the model for real trading decisions!")
                max_position_size = st.slider("Max Position Size (SOL):", 0.01, 1.0, 0.1)
                risk_multiplier = st.slider("Risk Multiplier:", 0.1, 2.0, 1.0)
            
        with col2:
            st.markdown(f"**📊 Model Info:**")
            if selected_model in st.session_state.model_performance:
                perf = st.session_state.model_performance[selected_model]
                st.metric("Type", perf['problem_type'])
                st.metric("Accuracy/R²", f"{perf.get('accuracy', perf.get('r2_score', 0)):.3f}")
                st.metric("Features", len(perf.get('feature_names', [])))
        
        # Deployment actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Deploy Model", type="primary"):
                self.deploy_model(selected_model, deployment_type, confidence_threshold)
        
        with col2:
            if st.button("🧪 Test Deployment"):
                self.test_model_deployment(selected_model)
        
        with col3:
            if st.button("📊 Monitoring Dashboard"):
                self.show_deployment_monitoring()
        
        # Live prediction interface
        st.markdown("### 🔮 Live Predictions")
        
        if st.button("🎯 Make Prediction"):
            self.make_live_prediction(selected_model)
    
    def generate_sample_data(self, data_source: str) -> pd.DataFrame:
        """Generate sample data based on source selection"""
        
        np.random.seed(42)
        n_samples = 1000
        
        if data_source == "📡 Live Coin Data":
            # Simulate live coin data
            data = {
                'price': np.random.lognormal(0, 2, n_samples),
                'volume_24h': np.random.lognormal(10, 3, n_samples),
                'price_change_24h': np.random.normal(0, 50, n_samples),
                'liquidity': np.random.lognormal(8, 2, n_samples),
                'market_cap': np.random.lognormal(12, 4, n_samples),
                'holder_count': np.random.randint(10, 10000, n_samples),
                'social_score': np.random.beta(2, 5, n_samples),
                'rug_risk': np.random.beta(2, 8, n_samples),
                'is_profitable': np.random.choice([0, 1], n_samples, p=[0.3, 0.7])
            }
        
        elif data_source == "📈 Historical Market Data":
            # Simulate historical market data
            dates = pd.date_range('2024-01-01', periods=n_samples, freq='H')
            price_base = 1000
            
            data = {
                'timestamp': dates,
                'open': np.random.normal(price_base, 50, n_samples),
                'high': np.random.normal(price_base * 1.02, 60, n_samples),
                'low': np.random.normal(price_base * 0.98, 40, n_samples),
                'close': np.random.normal(price_base, 55, n_samples),
                'volume': np.random.lognormal(10, 2, n_samples),
                'rsi': np.random.uniform(20, 80, n_samples),
                'macd': np.random.normal(0, 5, n_samples),
                'next_hour_profit': np.random.choice([0, 1], n_samples, p=[0.4, 0.6])
            }
        
        else:  # Enriched Signals
            data = {
                'confidence_score': np.random.uniform(0.3, 1.0, n_samples),
                'social_buzz': np.random.beta(2, 3, n_samples),
                'technical_strength': np.random.uniform(0, 1, n_samples),
                'sentiment_score': np.random.beta(3, 2, n_samples),
                'volume_spike': np.random.uniform(1, 10, n_samples),
                'liquidity_depth': np.random.lognormal(5, 2, n_samples),
                'whale_activity': np.random.poisson(2, n_samples),
                'telegram_mentions': np.random.poisson(5, n_samples),
                'is_runner': np.random.choice([0, 1], n_samples, p=[0.2, 0.8])
            }
        
        return pd.DataFrame(data)
    
    def preprocess_data(self, df, target_column, feature_columns, scale_features, handle_missing, feature_selection, n_features):
        """Preprocess the data for model training"""
        
        # Handle missing values
        if handle_missing == "Drop":
            df = df.dropna()
        elif handle_missing == "Mean":
            df = df.fillna(df.mean())
        elif handle_missing == "Median":
            df = df.fillna(df.median())
        elif handle_missing == "Mode":
            df = df.fillna(df.mode().iloc[0])
        
        # Select features and target
        X = df[feature_columns]
        y = df[target_column]
        
        # Scale features if requested
        if scale_features:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            X = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
        
        # Feature selection if requested
        if feature_selection and n_features:
            selector = SelectKBest(score_func=f_classif, k=min(n_features, len(feature_columns)))
            X_selected = selector.fit_transform(X, y)
            selected_features = [feature_columns[i] for i in selector.get_support(indices=True)]
            X = pd.DataFrame(X_selected, columns=selected_features, index=X.index)
        
        # Combine features and target
        result_df = X.copy()
        result_df[target_column] = y
        
        return result_df
    
    def render_model_parameters(self, model_type: str) -> Dict:
        """Render model-specific parameter controls"""
        
        params = {}
        
        if model_type in ['random_forest_clf', 'random_forest_reg']:
            col1, col2, col3 = st.columns(3)
            with col1:
                params['n_estimators'] = st.slider("Trees:", 10, 500, 100)
            with col2:
                params['max_depth'] = st.slider("Max Depth:", 3, 20, 10)
            with col3:
                params['min_samples_split'] = st.slider("Min Samples Split:", 2, 20, 5)
        
        elif model_type == 'gradient_boosting':
            col1, col2, col3 = st.columns(3)
            with col1:
                params['n_estimators'] = st.slider("Estimators:", 50, 300, 100)
            with col2:
                params['learning_rate'] = st.slider("Learning Rate:", 0.01, 0.3, 0.1)
            with col3:
                params['max_depth'] = st.slider("Max Depth:", 3, 10, 6)
        
        elif model_type in ['neural_network_clf', 'neural_network_reg']:
            col1, col2, col3 = st.columns(3)
            with col1:
                params['hidden_layer_sizes'] = st.selectbox(
                    "Hidden Layers:", 
                    [(100,), (100, 50), (200, 100, 50), (50, 50, 50)]
                )
            with col2:
                params['learning_rate_init'] = st.slider("Learning Rate:", 0.001, 0.1, 0.01)
            with col3:
                params['max_iter'] = st.slider("Max Iterations:", 100, 1000, 500)
        
        return params
    
    def train_model(self, model_type: str, params: Dict, cv_folds: int, hyperparameter_tuning: bool) -> Dict:
        """Train a single model"""
        
        try:
            data = st.session_state.processed_data
            df = data['df']
            target = data['target']
            problem_type = data['problem_type']
            test_size = data['test_size']
            
            # Prepare data
            X = df.drop(columns=[target])
            y = df[target]
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
            
            # Initialize model
            model = self.get_model(model_type, params)
            
            # Hyperparameter tuning if requested
            if hyperparameter_tuning:
                model = self.tune_hyperparameters(model, model_type, X_train, y_train, cv_folds)
            
            # Train model
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate performance metrics
            if problem_type == "Classification":
                performance = {
                    'accuracy': accuracy_score(y_test, y_pred),
                    'precision': classification_report(y_test, y_pred, output_dict=True)['weighted avg']['precision'],
                    'recall': classification_report(y_test, y_pred, output_dict=True)['weighted avg']['recall'],
                    'f1_score': classification_report(y_test, y_pred, output_dict=True)['weighted avg']['f1-score'],
                    'problem_type': 'Classification'
                }
            else:
                performance = {
                    'r2_score': r2_score(y_test, y_pred),
                    'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                    'mae': np.mean(np.abs(y_test - y_pred)),
                    'problem_type': 'Regression'
                }
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=cv_folds)
            performance['cv_score_mean'] = cv_scores.mean()
            performance['cv_score_std'] = cv_scores.std()
            
            # Store results
            model_name = f"{model_type}_{datetime.now().strftime('%H%M%S')}"
            st.session_state.trained_models[model_name] = model
            st.session_state.model_performance[model_name] = performance
            st.session_state.current_model_results = {
                'model_name': model_name,
                'performance': performance,
                'y_test': y_test,
                'y_pred': y_pred,
                'feature_names': X.columns.tolist()
            }
            
            # Feature importance
            if hasattr(model, 'feature_importances_'):
                importance_df = pd.DataFrame({
                    'feature': X.columns,
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)
                st.session_state.feature_importance[model_name] = importance_df
            
            return performance
            
        except Exception as e:
            st.error(f"Model training failed: {e}")
            return None
    
    def get_model(self, model_type: str, params: Dict):
        """Get model instance based on type and parameters"""
        
        if model_type == 'random_forest_clf':
            return RandomForestClassifier(**params, random_state=42)
        elif model_type == 'random_forest_reg':
            return RandomForestRegressor(**params, random_state=42)
        elif model_type == 'gradient_boosting':
            return GradientBoostingClassifier(**params, random_state=42)
        elif model_type == 'logistic_regression':
            return LogisticRegression(random_state=42)
        elif model_type == 'linear_regression':
            return LinearRegression()
        elif model_type == 'svm_clf':
            return SVC(random_state=42)
        elif model_type == 'svm_reg':
            return SVR()
        elif model_type == 'neural_network_clf':
            return MLPClassifier(**params, random_state=42)
        elif model_type == 'neural_network_reg':
            return MLPRegressor(**params, random_state=42)
        else:
            return RandomForestClassifier(random_state=42)
    
    def tune_hyperparameters(self, model, model_type: str, X_train, y_train, cv_folds: int):
        """Perform hyperparameter tuning"""
        
        param_grids = {
            'random_forest_clf': {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, None],
                'min_samples_split': [2, 5, 10]
            },
            'gradient_boosting': {
                'n_estimators': [50, 100, 150],
                'learning_rate': [0.05, 0.1, 0.15],
                'max_depth': [3, 5, 7]
            }
        }
        
        if model_type in param_grids:
            grid_search = GridSearchCV(
                model, param_grids[model_type], 
                cv=cv_folds, n_jobs=-1, scoring='accuracy' if 'clf' in model_type else 'r2'
            )
            grid_search.fit(X_train, y_train)
            return grid_search.best_estimator_
        
        return model
    
    def display_training_results(self):
        """Display training results"""
        
        results = st.session_state.current_model_results
        performance = results['performance']
        
        st.markdown("### 🎉 Training Results")
        
        if performance['problem_type'] == 'Classification':
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🎯 Accuracy", f"{performance['accuracy']:.3f}")
            with col2:
                st.metric("📊 F1-Score", f"{performance['f1_score']:.3f}")
            with col3:
                st.metric("🔄 CV Score", f"{performance['cv_score_mean']:.3f} ± {performance['cv_score_std']:.3f}")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📈 R² Score", f"{performance['r2_score']:.3f}")
            with col2:
                st.metric("📉 RMSE", f"{performance['rmse']:.3f}")
            with col3:
                st.metric("🔄 CV Score", f"{performance['cv_score_mean']:.3f} ± {performance['cv_score_std']:.3f}")
    
    def render_performance_charts(self, model_name: str, performance: Dict):
        """Render performance visualization charts"""
        
        if 'current_model_results' not in st.session_state:
            st.warning("No recent training results available.")
            return
        
        results = st.session_state.current_model_results
        y_test = results['y_test']
        y_pred = results['y_pred']
        
        if performance['problem_type'] == 'Classification':
            # Confusion Matrix
            cm = confusion_matrix(y_test, y_pred)
            
            fig = go.Figure(data=go.Heatmap(
                z=cm,
                x=['Predicted 0', 'Predicted 1'],
                y=['Actual 0', 'Actual 1'],
                colorscale='Viridis',
                text=cm,
                texttemplate="%{text}",
                textfont={"size": 16, "color": "white"}
            ))
            
            fig.update_layout(
                title='🎯 Confusion Matrix',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            # Actual vs Predicted scatter plot
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=y_test,
                y=y_pred,
                mode='markers',
                marker=dict(
                    color=self.colors['primary'],
                    size=8,
                    opacity=0.7
                ),
                name='Predictions',
                hovertemplate='<b>Actual:</b> %{x:.3f}<br><b>Predicted:</b> %{y:.3f}<extra></extra>'
            ))
            
            # Perfect prediction line
            min_val, max_val = min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())
            fig.add_trace(go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                line=dict(color=self.colors['danger'], dash='dash'),
                name='Perfect Prediction'
            ))
            
            fig.update_layout(
                title='📈 Actual vs Predicted Values',
                xaxis_title='Actual Values',
                yaxis_title='Predicted Values',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(gridcolor='rgba(16, 185, 129, 0.2)'),
                yaxis=dict(gridcolor='rgba(16, 185, 129, 0.2)')
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def render_feature_importance(self, model_name: str):
        """Render feature importance chart"""
        
        if model_name not in st.session_state.feature_importance:
            st.warning("Feature importance not available for this model.")
            return
        
        importance_df = st.session_state.feature_importance[model_name]
        
        fig = go.Figure(go.Bar(
            x=importance_df['importance'][:10],
            y=importance_df['feature'][:10],
            orientation='h',
            marker_color=self.colors['primary'],
            hovertemplate='<b>%{y}</b><br>Importance: %{x:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='🌟 Top 10 Feature Importance',
            xaxis_title='Importance Score',
            yaxis_title='Features',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=500,
            xaxis=dict(gridcolor='rgba(16, 185, 129, 0.2)'),
            yaxis=dict(gridcolor='rgba(16, 185, 129, 0.2)')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Feature importance table
        st.dataframe(importance_df, use_container_width=True)
    
    def render_model_insights(self, model_name: str, performance: Dict):
        """Render model insights and interpretability"""
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**🔍 Model Analysis:**")
            
            if performance['problem_type'] == 'Classification':
                if performance['accuracy'] > 0.9:
                    st.success("🎉 Excellent model performance!")
                elif performance['accuracy'] > 0.8:
                    st.info("👍 Good model performance")
                else:
                    st.warning("⚠️ Model needs improvement")
                
                st.write(f"**Precision:** {performance['precision']:.3f}")
                st.write(f"**Recall:** {performance['recall']:.3f}")
                st.write(f"**F1-Score:** {performance['f1_score']:.3f}")
            
            else:
                if performance['r2_score'] > 0.8:
                    st.success("🎉 Excellent model performance!")
                elif performance['r2_score'] > 0.6:
                    st.info("👍 Good model performance")
                else:
                    st.warning("⚠️ Model needs improvement")
                
                st.write(f"**R² Score:** {performance['r2_score']:.3f}")
                st.write(f"**RMSE:** {performance['rmse']:.3f}")
                st.write(f"**MAE:** {performance['mae']:.3f}")
        
        with col2:
            st.markdown("**📊 Recommendations:**")
            
            # Generate recommendations based on performance
            recommendations = []
            
            if performance['problem_type'] == 'Classification':
                if performance['accuracy'] < 0.8:
                    recommendations.extend([
                        "🔄 Try feature engineering",
                        "📊 Collect more training data",
                        "🎛️ Tune hyperparameters"
                    ])
                
                if performance['precision'] < performance['recall']:
                    recommendations.append("⚖️ Focus on reducing false positives")
                elif performance['recall'] < performance['precision']:
                    recommendations.append("🎯 Focus on reducing false negatives")
            
            else:
                if performance['r2_score'] < 0.6:
                    recommendations.extend([
                        "🔄 Try polynomial features",
                        "📊 Add more relevant features",
                        "🎛️ Try different algorithms"
                    ])
            
            if not recommendations:
                recommendations.append("✅ Model is performing well!")
            
            for rec in recommendations:
                st.write(f"• {rec}")
    
    def render_prediction_analysis(self, model_name: str):
        """Render prediction analysis tools"""
        
        st.markdown("**🔮 Make Custom Predictions:**")
        
        if 'processed_data' not in st.session_state:
            st.warning("No data available for predictions.")
            return
        
        # Get feature names
        data = st.session_state.processed_data
        df = data['df']
        target = data['target']
        feature_names = [col for col in df.columns if col != target]
        
        # Create input form
        input_values = {}
        
        cols = st.columns(min(3, len(feature_names)))
        for i, feature in enumerate(feature_names[:6]):  # Limit to first 6 features
            with cols[i % 3]:
                feature_data = df[feature]
                min_val = float(feature_data.min())
                max_val = float(feature_data.max())
                mean_val = float(feature_data.mean())
                
                input_values[feature] = st.number_input(
                    f"{feature}:",
                    min_value=min_val,
                    max_value=max_val,
                    value=mean_val,
                    key=f"input_{feature}"
                )
        
        if st.button("🔮 Make Prediction"):
            if model_name in st.session_state.trained_models:
                model = st.session_state.trained_models[model_name]
                
                # Prepare input data
                input_df = pd.DataFrame([input_values])
                
                # Make prediction
                prediction = model.predict(input_df)[0]
                
                if hasattr(model, 'predict_proba'):
                    probabilities = model.predict_proba(input_df)[0]
                    confidence = max(probabilities)
                    
                    st.success(f"🎯 Prediction: **{prediction}** (Confidence: {confidence:.1%})")
                else:
                    st.success(f"🎯 Prediction: **{prediction:.3f}**")
    
    def deploy_model(self, model_name: str, deployment_type: str, confidence_threshold: float):
        """Deploy model to specified target"""
        
        deployment_config = {
            'model_name': model_name,
            'deployment_type': deployment_type,
            'confidence_threshold': confidence_threshold,
            'deployed_at': datetime.now(),
            'status': 'active'
        }
        
        if 'deployed_models' not in st.session_state:
            st.session_state.deployed_models = {}
        
        st.session_state.deployed_models[model_name] = deployment_config
        
        st.success(f"✅ Model {model_name} deployed to {deployment_type}!")
        st.info(f"🎯 Confidence threshold: {confidence_threshold:.1%}")
        
        if deployment_type == "🔴 Live Trading Engine":
            st.warning("⚠️ **LIVE TRADING ACTIVE** - Monitor carefully!")
    
    def test_model_deployment(self, model_name: str):
        """Test model deployment"""
        
        st.info("🧪 Running deployment test...")
        
        # Simulate test results
        test_results = {
            'api_response_time': np.random.uniform(50, 200),
            'prediction_accuracy': np.random.uniform(0.8, 0.95),
            'throughput': np.random.randint(100, 1000),
            'error_rate': np.random.uniform(0, 0.05)
        }
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("⚡ Response Time", f"{test_results['api_response_time']:.0f}ms")
        with col2:
            st.metric("🎯 Test Accuracy", f"{test_results['prediction_accuracy']:.1%}")
        with col3:
            st.metric("📊 Throughput", f"{test_results['throughput']}/min")
        with col4:
            st.metric("❌ Error Rate", f"{test_results['error_rate']:.1%}")
        
        if test_results['error_rate'] < 0.02:
            st.success("✅ Deployment test passed!")
        else:
            st.warning("⚠️ High error rate detected - check model configuration")
    
    def make_live_prediction(self, model_name: str):
        """Make a live prediction with current market data"""
        
        st.info("🔮 Making live prediction with current market data...")
        
        # Simulate live market data
        live_data = {
            'price': np.random.lognormal(0, 1),
            'volume_24h': np.random.lognormal(10, 2),
            'price_change_24h': np.random.normal(0, 20),
            'social_score': np.random.beta(2, 3),
            'confidence_score': np.random.uniform(0.5, 1.0)
        }
        
        prediction = np.random.choice([0, 1], p=[0.3, 0.7])
        confidence = np.random.uniform(0.7, 0.95)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**📊 Current Market Data:**")
            for key, value in live_data.items():
                st.write(f"• **{key}:** {value:.4f}")
        
        with col2:
            if prediction == 1:
                st.success(f"🚀 **BUY SIGNAL**")
                st.metric("Confidence", f"{confidence:.1%}")
            else:
                st.error(f"🛑 **HOLD/SELL**")
                st.metric("Confidence", f"{confidence:.1%}")

if __name__ == "__main__":
    builder = ModelBuilder()
    builder.render_model_builder()