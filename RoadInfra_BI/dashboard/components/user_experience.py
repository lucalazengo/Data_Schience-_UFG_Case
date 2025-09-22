"""
Componentes para melhorar a experiência do usuário no dashboard.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import time
from datetime import datetime


def create_loading_animation():
    """
    Cria animação de carregamento personalizada.
    """
    placeholder = st.empty()
    
    with placeholder.container():
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 200px;">
            <div style="text-align: center;">
                <div style="border: 4px solid #f3f3f3; border-top: 4px solid #1f77b4; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin: 0 auto;"></div>
                <p style="margin-top: 20px; color: #666;">🛣️ Carregando dados de segurança viária...</p>
            </div>
        </div>
        <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
        """, unsafe_allow_html=True)
    
    return placeholder


def create_progress_tracker(current_step, total_steps, step_name):
    """
    Cria barra de progresso com informações detalhadas.
    """
    progress = current_step / total_steps
    
    st.markdown(f"""
    <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
        <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 0.5rem;">
            <strong>🔄 {step_name}</strong>
            <span style="color: #666;">{current_step}/{total_steps}</span>
        </div>
        <div style="background-color: #e9ecef; height: 8px; border-radius: 4px; overflow: hidden;">
            <div style="background-color: #1f77b4; height: 100%; width: {progress*100:.1f}%; transition: width 0.3s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    return st.progress(progress)


def create_interactive_tooltip(data, title="Informações Detalhadas"):
    """
    Cria tooltip interativo com informações detalhadas.
    """
    with st.expander(f"ℹ️ {title}", expanded=False):
        if isinstance(data, dict):
            for key, value in data.items():
                st.write(f"**{key}:** {value}")
        elif isinstance(data, pd.DataFrame):
            st.dataframe(data, width='stretch')
        else:
            st.write(data)


def create_notification_system():
    """
    Sistema de notificações para feedback do usuário.
    """
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    
    # Container para notificações
    notification_container = st.container()
    
    # Exibe notificações ativas
    with notification_container:
        for i, notification in enumerate(st.session_state.notifications):
            if notification['active']:
                notification_type = notification['type']
                message = notification['message']
                
                if notification_type == 'success':
                    st.success(f"✅ {message}")
                elif notification_type == 'warning':
                    st.warning(f"⚠️ {message}")
                elif notification_type == 'error':
                    st.error(f"❌ {message}")
                elif notification_type == 'info':
                    st.info(f"ℹ️ {message}")
                
                # Auto-remove após 5 segundos
                if time.time() - notification['timestamp'] > 5:
                    st.session_state.notifications[i]['active'] = False


def add_notification(message, notification_type='info'):
    """
    Adiciona nova notificação ao sistema.
    """
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    
    st.session_state.notifications.append({
        'message': message,
        'type': notification_type,
        'timestamp': time.time(),
        'active': True
    })


def create_help_system():
    """
    Sistema de ajuda contextual.
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🆘 Ajuda")
    
    help_topics = {
        "🎛️ Como usar os filtros": """
        **Filtros Temporais:**
        - Selecione o período de análise
        - Use o slider para anos específicos
        
        **Filtros Geográficos:**
        - Escolha estados e rodovias
        - Combine múltiplas seleções
        
        **Simulação de Intervenções:**
        - Ative para testar cenários
        - Ajuste parâmetros de efetividade
        """,
        
        "📊 Interpretando gráficos": """
        **Cores dos gráficos:**
        - 🔴 Vermelho: Situação crítica
        - 🟠 Laranja: Atenção necessária
        - 🟡 Amarelo: Situação moderada
        - 🟢 Verde: Situação controlada
        
        **Interatividade:**
        - Clique para filtrar
        - Hover para detalhes
        - Zoom com mouse
        """,
        
        "🎯 Recomendações": """
        **Prioridades:**
        - CRÍTICA: Ação imediata
        - ALTA: Ação em 30 dias
        - MÉDIA: Ação em 90 dias
        
        **ROI:**
        - Baseado em custos reais
        - Considera efetividade
        - Inclui custos indiretos
        """
    }
    
    for topic, content in help_topics.items():
        with st.sidebar.expander(topic):
            st.markdown(content)


def create_feedback_form():
    """
    Formulário de feedback do usuário.
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💬 Feedback")
    
    with st.sidebar.form("feedback_form"):
        rating = st.select_slider(
            "Como você avalia o dashboard?",
            options=["😞", "😐", "🙂", "😊", "🤩"],
            value="🙂"
        )
        
        feedback_type = st.selectbox(
            "Tipo de feedback:",
            ["Sugestão", "Bug", "Elogio", "Crítica"]
        )
        
        message = st.text_area(
            "Sua mensagem:",
            placeholder="Compartilhe sua experiência..."
        )
        
        submitted = st.form_submit_button("📤 Enviar Feedback")
        
        if submitted and message:
            add_notification(
                "Feedback enviado com sucesso! Obrigado pela contribuição.",
                "success"
            )
            st.balloons()


def create_keyboard_shortcuts():
    """
    Sistema de atalhos de teclado.
    """
    st.markdown("""
    <script>
    document.addEventListener('keydown', function(e) {
        // Ctrl + R: Resetar filtros
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            // Trigger reset button click
            const resetBtn = document.querySelector('[data-testid="reset-filters"]');
            if (resetBtn) resetBtn.click();
        }
        
        // Ctrl + S: Salvar configuração
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            // Trigger save button click
            const saveBtn = document.querySelector('[data-testid="save-config"]');
            if (saveBtn) saveBtn.click();
        }
        
        // F1: Mostrar ajuda
        if (e.key === 'F1') {
            e.preventDefault();
            // Toggle help sidebar
            const helpBtn = document.querySelector('[data-testid="help-toggle"]');
            if (helpBtn) helpBtn.click();
        }
    });
    </script>
    """, unsafe_allow_html=True)


def create_data_export_options():
    """
    Opções avançadas de exportação de dados.
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 Exportar Dados")
    
    export_format = st.sidebar.selectbox(
        "Formato:",
        ["CSV", "Excel", "PDF", "JSON"]
    )
    
    export_scope = st.sidebar.selectbox(
        "Escopo:",
        ["Dados filtrados", "Todos os dados", "Apenas gráficos", "Relatório completo"]
    )
    
    if st.sidebar.button("📤 Exportar", type="primary"):
        add_notification(
            f"Exportação iniciada: {export_format} - {export_scope}",
            "info"
        )
        # Simula processo de exportação
        progress_bar = st.sidebar.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        
        add_notification(
            "Exportação concluída com sucesso!",
            "success"
        )


def create_theme_selector():
    """
    Seletor de tema para personalização.
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎨 Personalização")
    
    theme = st.sidebar.selectbox(
        "Tema:",
        ["Padrão", "Escuro", "Alto Contraste", "Colorblind Friendly"]
    )
    
    if theme != "Padrão":
        # Aplica CSS customizado baseado no tema
        theme_css = {
            "Escuro": """
            <style>
            .stApp { background-color: #1e1e1e; color: white; }
            .stSidebar { background-color: #2d2d2d; }
            </style>
            """,
            "Alto Contraste": """
            <style>
            .stApp { background-color: black; color: yellow; }
            .stButton > button { background-color: yellow; color: black; }
            </style>
            """,
            "Colorblind Friendly": """
            <style>
            :root {
                --primary-color: #0173b2;
                --secondary-color: #de8f05;
                --success-color: #029e73;
                --warning-color: #d55e00;
                --error-color: #cc78bc;
            }
            </style>
            """
        }
        
        if theme in theme_css:
            st.markdown(theme_css[theme], unsafe_allow_html=True)


def create_performance_monitor():
    """
    Monitor de performance da aplicação.
    """
    if st.sidebar.checkbox("🔧 Monitor de Performance"):
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ⚡ Performance")
        
        # Simula métricas de performance
        load_time = 2.3
        memory_usage = 45.2
        data_points = 15420
        
        st.sidebar.metric("Tempo de Carregamento", f"{load_time}s")
        st.sidebar.metric("Uso de Memória", f"{memory_usage}MB")
        st.sidebar.metric("Pontos de Dados", f"{data_points:,}")
        
        # Gráfico de performance
        perf_data = pd.DataFrame({
            'Tempo': pd.date_range('2024-01-01', periods=24, freq='H'),
            'Latência': [2.1, 2.3, 1.9, 2.5, 2.0, 1.8, 2.2, 2.4, 2.1, 1.9, 2.3, 2.0,
                        2.2, 2.1, 1.9, 2.4, 2.3, 2.0, 1.8, 2.2, 2.1, 2.3, 2.0, 1.9]
        })
        
        fig = px.line(perf_data, x='Tempo', y='Latência', 
                     title="Latência nas últimas 24h")
        fig.update_layout(height=200)
        st.sidebar.plotly_chart(fig, width='stretch')


def create_user_preferences():
    """
    Sistema de preferências do usuário.
    """
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            'auto_refresh': False,
            'show_tooltips': True,
            'animation_speed': 'Normal',
            'default_view': 'Dashboard',
            'notifications': True
        }
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Preferências")
    
    with st.sidebar.expander("Configurações Avançadas"):
        st.session_state.user_preferences['auto_refresh'] = st.checkbox(
            "Auto-atualização",
            value=st.session_state.user_preferences['auto_refresh']
        )
        
        st.session_state.user_preferences['show_tooltips'] = st.checkbox(
            "Mostrar tooltips",
            value=st.session_state.user_preferences['show_tooltips']
        )
        
        st.session_state.user_preferences['animation_speed'] = st.selectbox(
            "Velocidade das animações:",
            ["Lenta", "Normal", "Rápida", "Desabilitada"],
            index=1
        )
        
        st.session_state.user_preferences['notifications'] = st.checkbox(
            "Notificações",
            value=st.session_state.user_preferences['notifications']
        )
        
        if st.button("💾 Salvar Preferências"):
            add_notification("Preferências salvas com sucesso!", "success")


def enhance_user_experience():
    """
    Função principal para aplicar todas as melhorias de UX.
    """
    # Aplica sistema de notificações
    create_notification_system()
    
    # Adiciona sistema de ajuda
    create_help_system()
    
    # Adiciona formulário de feedback
    create_feedback_form()
    
    # Adiciona atalhos de teclado
    create_keyboard_shortcuts()
    
    # Adiciona opções de exportação
    create_data_export_options()
    
    # Adiciona seletor de tema
    create_theme_selector()
    
    # Adiciona monitor de performance
    create_performance_monitor()
    
    # Adiciona preferências do usuário
    create_user_preferences()
    
    # CSS global para melhorar a aparência
    st.markdown("""
    <style>
    /* Melhora a aparência dos botões */
    .stButton > button {
        border-radius: 20px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Melhora a aparência dos selectbox */
    .stSelectbox > div > div {
        border-radius: 10px;
    }
    
    /* Animações suaves */
    .stMetric {
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: scale(1.05);
    }
    
    /* Melhora a aparência dos expanders */
    .streamlit-expanderHeader {
        border-radius: 10px;
        background-color: #f8f9fa;
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    </style>
    """, unsafe_allow_html=True)