import streamlit as st
import json
import os
from datetime import datetime

class DragonTigerAnalyzer:
    def __init__(self):
        self.history = []
        self.signals = []
        self.performance = {'total': 0, 'hits': 0, 'misses': 0}
        self.load_data()

    def add_outcome(self, outcome):
        """Adiciona um novo resultado ao histórico e dispara a análise."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.history.append((timestamp, outcome))
        is_correct = self.verify_previous_prediction(outcome)
        pattern, prediction = self.detect_pattern()

        if pattern is not None:
            self.signals.append({
                'time': timestamp,
                'pattern': pattern,
                'prediction': prediction,
                'correct': None
            })

        self.save_data()
        return pattern, prediction, is_correct

    def verify_previous_prediction(self, current_outcome):
        """Verifica se a última sugestão foi correta e atualiza as métricas."""
        for i in reversed(range(len(self.signals))):
            signal = self.signals[i]
            if signal.get('correct') is None:
                if signal['prediction'] == current_outcome:
                    self.performance['hits'] += 1
                    self.performance['total'] += 1
                    signal['correct'] = "✅"
                    return "✅"
                else:
                    self.performance['misses'] += 1
                    self.performance['total'] += 1
                    signal['correct'] = "❌"
                    return "❌"
        return None

    def undo_last(self):
        """Desfaz o último resultado e a última sugestão."""
        if self.history:
            removed_time, _ = self.history.pop()
            if self.signals and self.signals[-1]['time'] == removed_time:
                removed_signal = self.signals.pop()
                if removed_signal.get('correct') == "✅":
                    self.performance['hits'] = max(0, self.performance['hits'] - 1)
                    self.performance['total'] = max(0, self.performance['total'] - 1)
                elif removed_signal.get('correct') == "❌":
                    self.performance['misses'] = max(0, self.performance['misses'] - 1)
                    self.performance['total'] = max(0, self.performance['total'] - 1)
            self.save_data()
            return True
        return False

    def clear_history(self):
        """Limpa todo o histórico e as métricas."""
        self.history = []
        self.signals = []
        self.performance = {'total': 0, 'hits': 0, 'misses': 0}
        self.save_data()

    def detect_pattern(self):
        """
        Detecta padrões no histórico com base na lista de 30 padrões fornecida,
        priorizando os mais longos e mais fortes.
        """
        if len(self.history) < 2:
            return None, None

        outcomes = [outcome for _, outcome in self.history]
        n = len(outcomes)

        # ----------------------------------------------------
        # 1. Padrões de Repetição (Streaks)
        # ----------------------------------------------------
        # Padrão 1: Dragon Streak (4 ou mais)
        if n >= 4 and outcomes[-4:] == ['H', 'H', 'H', 'H']:
            return 1, 'H'

        # Padrão 2: Tiger Streak (4 ou mais)
        if n >= 4 and outcomes[-4:] == ['A', 'A', 'A', 'A']:
            return 2, 'A'
            
        # Padrão 3: Long Streak Breaker (após 5 vitórias, sugere o lado oposto)
        if n >= 6 and outcomes[-6:-1] == ['H', 'H', 'H', 'H', 'H']:
            return 3, 'A'
        if n >= 6 and outcomes[-6:-1] == ['A', 'A', 'A', 'A', 'A']:
            return 3, 'H'

        # Padrão 5: Broken Streak (com interrupção de Tie)
        if n >= 5 and outcomes[-5:] == ['H', 'H', 'T', 'H', 'H']:
            return 5, 'H'
        if n >= 5 and outcomes[-5:] == ['A', 'A', 'T', 'A', 'A']:
            return 5, 'A'
            
        # ----------------------------------------------------
        # 2. Padrões Alternados (Zig-Zag e Variantes)
        # ----------------------------------------------------
        # Padrão 6: Zig-Zag Simples (alternância direta)
        if n >= 4 and outcomes[-4:] == ['H', 'A', 'H', 'A']:
            return 6, 'H'
        if n >= 4 and outcomes[-4:] == ['A', 'H', 'A', 'H']:
            return 6, 'A'

        # Padrão 8: Zig-Zag Duplo
        if n >= 6 and outcomes[-6:] == ['H', 'H', 'A', 'A', 'H', 'H']:
            return 8, 'A'
        if n >= 6 and outcomes[-6:] == ['A', 'A', 'H', 'H', 'A', 'A']:
            return 8, 'H'
            
        # ----------------------------------------------------
        # 3. Padrões de Blocos (Grupos de Vitórias)
        # ----------------------------------------------------
        # Padrão 12: Blocos de 3
        if n >= 6 and outcomes[-6:] == ['H', 'H', 'H', 'A', 'A', 'A']:
            return 12, 'H'
        if n >= 6 and outcomes[-6:] == ['A', 'A', 'A', 'H', 'H', 'H']:
            return 12, 'A'

        # Padrão 13: Espelho Curto
        if n >= 6 and outcomes[-3:] == outcomes[-6:-3]:
            return 13, outcomes[-3]
            
        # Padrão 14: Espelho Longo
        if n >= 8 and outcomes[-4:] == outcomes[-8:-4]:
            return 14, outcomes[-4]

        # Padrão 15: Reflexo Oposto
        if n >= 8 and outcomes[-8:] == ['H', 'H', 'A', 'A', 'T', 'T', 'H', 'H']:
            return 15, 'A'
        if n >= 8 and outcomes[-8:] == ['A', 'A', 'H', 'H', 'T', 'T', 'A', 'A']:
            return 15, 'H'

        # ----------------------------------------------------
        # 4. Padrões de Empate (Tie)
        # ----------------------------------------------------
        # Padrão 17: Tie Duplo
        if n >= 2 and outcomes[-2:] == ['T', 'T']:
            # Sugere o oposto do que veio antes do Tie duplo, se houver
            if n > 2:
                return 17, 'H' if outcomes[-3] == 'A' else 'A'
            return 17, None # Nenhum padrão claro para seguir após o Tie Duplo

        # ----------------------------------------------------
        # 5. Padrões por Frequência / Tendência
        # ----------------------------------------------------
        last_10_outcomes = outcomes[-10:]
        h_count = last_10_outcomes.count('H')
        a_count = last_10_outcomes.count('A')
        
        # Padrão 21: Dominância do Dragon (80% em 10 rodadas)
        if h_count >= 8:
            return 21, 'H'
            
        # Padrão 22: Dominância do Tiger (80% em 10 rodadas)
        if a_count >= 8:
            return 22, 'A'

        # ----------------------------------------------------
        # 6. Padrões Compostos / Avançados (simplificados)
        # ----------------------------------------------------
        # Padrão 28: Multiplicação por Bloco
        if n >= 4 and outcomes[-4:] == ['H', 'A', 'H', 'A']:
            return 28, 'H'
        if n >= 4 and outcomes[-4:] == ['A', 'H', 'A', 'H']:
            return 28, 'A'

        # ----------------------------------------------------
        # Padrões menores e de menor prioridade (do sistema anterior)
        # ----------------------------------------------------
        # Repetição de 3
        if n >= 3 and outcomes[-3:] == ['H', 'H', 'H']:
            return 31, 'H'
        if n >= 3 and outcomes[-3:] == ['A', 'A', 'A']:
            return 31, 'A'

        # Padrão H-H-A
        if n >= 3 and outcomes[-3:] == ['H', 'H', 'A']:
            return 32, 'H'
        if n >= 3 and outcomes[-3:] == ['A', 'A', 'H']:
            return 32, 'A'
        
        # Padrão H-A-H
        if n >= 3 and outcomes[-3:] == ['H', 'A', 'H']:
            return 33, 'A'
        if n >= 3 and outcomes[-3:] == ['A', 'H', 'A']:
            return 33, 'H'
            
        # Padrão de alternância simples
        if n >= 2 and outcomes[-1] != outcomes[-2]:
            return 34, outcomes[-1]


        return None, None

    def load_data(self):
        """Carrega os dados salvos de um arquivo JSON."""
        if os.path.exists('analyzer_data.json'):
            with open('analyzer_data.json', 'r') as f:
                try:
                    data = json.load(f)
                    self.history = data.get('history', [])
                    self.signals = data.get('signals', [])
                    self.performance = data.get('performance', {'total': 0, 'hits': 0, 'misses': 0})
                except json.JSONDecodeError:
                    st.warning("Arquivo de dados corrompido. Reiniciando o histórico.")
                    self.history = []
                    self.signals = []
                    self.performance = {'total': 0, 'hits': 0, 'misses': 0}
        else:
            self.save_data()

    def save_data(self):
        """Salva o estado atual do histórico e das métricas em um arquivo JSON."""
        data = {
            'history': self.history,
            'signals': self.signals,
            'performance': self.performance
        }
        with open('analyzer_data.json', 'w') as f:
            json.dump(data, f, indent=4)

    def get_accuracy(self):
        """Calcula a acurácia do sistema."""
        if self.performance['total'] == 0:
            return 0.0
        return (self.performance['hits'] / self.performance['total']) * 100

# Inicialização do aplicativo
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = DragonTigerAnalyzer()

# Interface do Streamlit
st.set_page_config(page_title="Dragon Tiger Analyzer", layout="wide", page_icon="🐉")
st.title("🐉 Dragon Tiger Analyzer Pro")
st.subheader("Sistema de detecção de padrões para Dragon Tiger")

st.markdown("---")

## Registrar Resultado da Rodada

st.write("Para registrar o resultado da última rodada, selecione uma das opções abaixo:")
st.markdown("<br>", unsafe_allow_html=True)
st.write("**Qual foi o resultado da última rodada?**")

cols_outcome = st.columns(3)
with cols_outcome[0]:
    # Botão para DRAGÃO (VERMELHO)
    if st.button("🔴 Dragão", use_container_width=True, type="primary"):
        st.session_state.analyzer.add_outcome('H')
        st.rerun()
with cols_outcome[1]:
    # Botão para TIGRE (AMARELO)
    # A cor primária do Streamlit é azul, então usamos apenas o emoji para a cor.
    if st.button("🟡 Tigre", use_container_width=True):
        st.session_state.analyzer.add_outcome('A')
        st.rerun()
with cols_outcome[2]:
    # Botão para EMPATE (VERDE)
    # A cor primária do Streamlit é azul, então usamos apenas o emoji para a cor.
    if st.button("🟢 Empate", use_container_width=True):
        st.session_state.analyzer.add_outcome('T')
        st.rerun()

st.markdown("---")
st.subheader("Controles do Histórico")
cols_controls = st.columns(2)
with cols_controls[0]:
    if st.button("↩️ Desfazer Último", use_container_width=True):
        st.session_state.analyzer.undo_last()
        st.rerun()
with cols_controls[1]:
    if st.button("🗑️ Limpar Tudo", use_container_width=True, type="secondary"):
        st.session_state.analyzer.clear_history()
        st.rerun()

st.markdown("---")

## Sugestão para a Próxima Rodada

current_pattern, current_prediction = st.session_state.analyzer.detect_pattern()

if current_prediction:
    display_prediction = ""
    bg_color_prediction = ""
    if current_prediction == 'H':
        display_prediction = "🔴 DRAGÃO"
        # Cor de fundo para o Dragão (Vermelho)
        bg_color_prediction = "rgba(255, 0, 0, 0.2)"
    elif current_prediction == 'A':
        display_prediction = "🟡 TIGRE"
        # Cor de fundo para o Tigre (Amarelo)
        bg_color_prediction = "rgba(255, 255, 0, 0.2)"
    else:
        display_prediction = "🟢 EMPATE"
        # Cor de fundo para o Empate (Verde)
        bg_color_prediction = "rgba(0, 128, 0, 0.2)"

    st.markdown(f"""
    <div style="
        background: {bg_color_prediction};
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        border: 2px solid #fff;
    ">
        <div style="font-size: 20px; font-weight: bold; margin-bottom: 10px;">
            Sugestão Baseada no Padrão {current_pattern}:
        </div>
        <div style="font-size: 40px; font-weight: bold; color: #fff; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
            {display_prediction}
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Registre pelo menos 2 resultados para ver uma sugestão para a próxima rodada.")

st.markdown("---")

## Métricas de Desempenho

accuracy = st.session_state.analyzer.get_accuracy()
col1, col2, col3 = st.columns(3)
col1.metric("Acurácia", f"{accuracy:.2f}%" if st.session_state.analyzer.performance['total'] > 0 else "0%")
col2.metric("Total de Previsões", st.session_state.analyzer.performance['total'])
col3.metric("Acertos", st.session_state.analyzer.performance['hits'])

st.markdown("---")

## Histórico de Resultados

st.caption("Mais recente → Mais antigo (esquerda → direita)")

if st.session_state.analyzer.history:
    outcomes = [outcome for _, outcome in st.session_state.analyzer.history][::-1][:72]
    total = len(outcomes)
    
    num_cols = 9
    num_rows = (total + num_cols - 1) // num_cols
    
    for row in range(num_rows):
        cols = st.columns(num_cols)
        start = row * num_cols
        end = min(start + num_cols, total)

        for i in range(start, end):
            outcome = outcomes[i]
            # Atualiza os emojis para refletir as novas cores
            emoji = "🔴" if outcome == 'H' else "🟡" if outcome == 'A' else "🟢"
            with cols[i - start]:
                st.markdown(f"<div style='font-size: 24px; text-align: center;'>{emoji}</div>", unsafe_allow_html=True)
else:
    st.info("Nenhum resultado registrado. Use os botões acima para começar.")

st.markdown("---")

## Últimas Sugestões/Previsões

if st.session_state.analyzer.signals:
    for signal in st.session_state.analyzer.signals[-5:][::-1]:
        display = ""
        bg_color = ""
        if signal['prediction'] == 'H':
            display = "🔴 DRAGÃO"
            # Cor de fundo para o Dragão (Vermelho)
            bg_color = "rgba(255, 0, 0, 0.1)"
        elif signal['prediction'] == 'A':
            display = "🟡 TIGRE"
            # Cor de fundo para o Tigre (Amarelo)
            bg_color = "rgba(255, 255, 0, 0.1)"
        else:
            display = "🟢 EMPATE"
            # Cor de fundo para o Empate (Verde)
            bg_color = "rgba(0, 128, 0, 0.1)"

        status = signal.get('correct', '')
        color = "green" if status == "✅" else "red" if status == "❌" else "gray"

        st.markdown(f"""
        <div style="
            background: {bg_color};
            border-radius: 10px;
            padding: 12px;
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        ">
            <div><strong>Padrão {signal['pattern']}</strong></div>
            <div style="font-size: 24px; font-weight: bold;">{display}</div>
            <div style="color: {color}; font-weight: bold; font-size: 24px;">{status}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Registre resultados para gerar sugestões. Após 2+ rodadas, as previsões aparecerão aqui.")

