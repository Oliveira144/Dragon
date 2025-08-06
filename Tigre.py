import streamlit as st
import collections

# --- Configuração da página ---
st.set_page_config(
    page_title="Analisador de Padrões Dragon Tiger",
    page_icon="🐉🐯",
    layout="wide"
)

# --- Variáveis de Mapeamento ---
mapear_emojis = {'D': '🐉', 'T': '🐯', 'E': '🟡'}

# --- Funções de Análise de Padrões ---
def analisar_padrao_dragon_tiger(historico):
    """
    Analisa o histórico do Dragon Tiger e retorna o padrão detectado e a sugestão de aposta.
    Prioriza a detecção de padrões de Empate e dos 8 padrões principais.
    """
    if len(historico) < 2:
        return "Nenhum Padrão Detectado", "Aguardando...", "Insira mais resultados para iniciar a análise."

    # Invertemos o histórico para analisar do mais recente para o mais antigo
    hist_recente = list(historico)[::-1]

    # --- ANÁLISE PRIORITÁRIA DE EMPATES (🟡) ---
    # 6. Padrão Tie Âncora (Empate inserido para quebrar a leitura)
    # Aposta: Alta probabilidade de repetir o lado anterior.
    if len(hist_recente) >= 2 and hist_recente[0] == 'E' and hist_recente[1] in ['D', 'T']:
        lado_anterior = mapear_emojis[hist_recente[1]]
        sugestao_completa = f"**Padrão Tie Âncora.** Um empate foi usado para resetar a leitura. A IA geralmente força a repetição do lado anterior para confundir. Prepare-se para um novo ciclo."
        return "Tie Âncora", f"Aposte em {lado_anterior} (Repetição do lado anterior)", sugestao_completa

    # 9. Padrão Âncora com Delay (Empate no meio de alternâncias)
    # Aposta: Repetição do lado anterior é comum.
    if len(hist_recente) >= 3 and hist_recente[1] == 'E' and hist_recente[0] != hist_recente[2]:
        lado_anterior = mapear_emojis[hist_recente[2]]
        sugestao_completa = f"**Padrão Âncora com Delay.** Um empate no meio de alternâncias. A IA continua a alternância. A sugestão é seguir a alternância, mas com cautela, pois o empate pode ter quebrado a leitura."
        return "Âncora com Delay", f"Aposte em {lado_anterior} (Seguir alternância)", sugestao_completa
        
    # --- ANÁLISE DOS PADRÕES PRINCIPAIS E SUBPADRÕES ---
    # Garante que não há empates nas últimas 5 jogadas para evitar conflito com a lógica acima
    if 'E' not in hist_recente[:5]:
        # 1. Padrão Alternância (Zig-Zag)
        count_alternancia = 0
        for i in range(min(len(hist_recente) - 1, 6)): # Limita a 6 para evitar falsos positivos
            if hist_recente[i] != hist_recente[i+1]:
                count_alternancia += 1
            else:
                break
        if count_alternancia >= 3:
            sugestao_completa = f"**Padrão Alternância (Zig-Zag)** com {count_alternancia + 1} sequências. A IA está preparando uma quebra. Sugestão: Prepare-se para apostar na repetição do lado vencedor da última rodada."
            return "Alternância (Zig-Zag)", f"Prepare-se para a quebra. Aposte em {mapear_emojis[hist_recente[0]]}", sugestao_completa

        # 2. Padrão Streak (Sequência Longa)
        count_streak = 0
        for i in range(min(len(hist_recente), 8)): # Limita a 8 repetições
            if hist_recente[i] == hist_recente[0]:
                count_streak += 1
            else:
                break
        if count_streak >= 4:
            sugestao_completa = f"**Padrão Streak** com {count_streak} vitórias consecutivas. A IA cria confiança falsa. A quebra pode ocorrer a qualquer momento. Sugestão: Aposte na continuidade com cautela ou espere a quebra para inverter."
            return "Streak (Sequência Longa)", f"Aposte em {mapear_emojis[hist_recente[0]]} (com cautela)", sugestao_completa

        # 3. Padrão Espelhado (Mirror)
        # Ex: D-D-T-T-T-T-D-D
        if len(hist_recente) >= 4 and hist_recente[0:2] == hist_recente[2:4][::-1] and hist_recente[0] != hist_recente[2]:
            sugestao_completa = "**Padrão Espelhado.** A IA inverte a sequência para confundir sua leitura. Sugestão: Aposte contra a repetição exata do espelho."
            return "Espelhado (Mirror)", f"Aposte em {mapear_emojis[hist_recente[1]]} (Contra o espelho)", sugestao_completa

        # 4. Padrão Gradual (Escada)
        if len(hist_recente) >= 6:
            # Ex: D-T-T-D-D-D-T-T-T-T
            # Verifica se a sequência recente mostra um lado crescendo
            bloco_1 = hist_recente[0]
            bloco_2 = hist_recente[3]
            bloco_3 = hist_recente[6]
            if hist_recente[0:2].count(bloco_1) >= 2 and hist_recente[2:5].count(bloco_2) >= 3 and hist_recente[5:].count(bloco_3) >= 4:
                sugestao_completa = f"**Padrão Gradual (Escada).** A IA está simulando naturalidade. A aposta mais segura é no lado que está crescendo. Prepare a quebra após 4 vitórias seguidas."
                return "Gradual (Escada)", f"Aposte em {mapear_emojis[hist_recente[0]]} até 4 vitórias", sugestao_completa
        
        # 5. Padrão Cluster (Blocos Curtos)
        if len(hist_recente) >= 6:
            # Ex: (D-D-T) (T-T-D) (D-D-T)
            bloco_1 = tuple(hist_recente[0:3])
            bloco_2 = tuple(hist_recente[3:6])
            if bloco_1 == bloco_2:
                sugestao_completa = f"**Padrão Cluster.** A IA cria uma sensação de pseudoaleatoriedade. Sugestão: Aposte na repetição do bloco, mas prepare-se para inverter após o terceiro bloco."
                return "Cluster (Blocos Curtos)", f"Aposte em {mapear_emojis[bloco_1[0]]} (Repetição do bloco)", sugestao_completa
        
        # 7. Padrão Falso Ciclo
        if len(hist_recente) >= 4 and hist_recente[0] == hist_recente[2] and hist_recente[1] == hist_recente[3] and hist_recente[0] != hist_recente[1]:
            sugestao_completa = f"**Padrão Falso Ciclo.** A IA está simulando um ciclo previsível para quebrar no final. Sugestão: Aposte na quebra do ciclo."
            return "Falso Ciclo", f"Aposte na quebra. Sugestão: Aposte em {mapear_emojis[hist_recente[0]]}", sugestao_completa

    # --- PADRÃO PADRÃO CAMUFLADO (PSEUDO-RANDOM) ---
    # É o padrão "catch-all" quando nada mais se encaixa
    sugestao_completa = "**Padrão Camuflado (Pseudo-Random).** A IA está misturando padrões para criar uma ilusão de caos total. Sugestão: Use a contagem estatística (contagem dos últimos 10) para apostar no lado que está levemente atrás."
    contagem = collections.Counter(historico)
    if 'D' in contagem and 'T' in contagem:
        lado_atras = 'D' if contagem['D'] < contagem['T'] else 'T'
        sugestao_direta = f"Aposte no lado que está levemente atrás: {mapear_emojis[lado_atras]}"
    else:
        sugestao_direta = "Cautela! Não aposte pesado"
    return "Camuflado (Pseudo-Random)", sugestao_direta, sugestao_completa

# --- Inicialização do estado da sessão ---
if 'historico' not in st.session_state:
    st.session_state.historico = collections.deque(maxlen=20) # Limita a 20 resultados

# --- Layout do aplicativo ---
st.title("🐉🐯 Analisador de Padrões Dragon Tiger")
st.markdown("---")

st.markdown("### 1. Inserir Resultados")
st.write("Clique nos botões correspondentes ao resultado do jogo. 'Dragon' e 'Tiger' são os 'Lados'.")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🐉 Dragon", use_container_width=True):
        st.session_state.historico.append('D')
with col2:
    if st.button("🐯 Tiger", use_container_width=True):
        st.session_state.historico.append('T')
with col3:
    if st.button("🟡 Empate", use_container_width=True):
        st.session_state.historico.append('E')
with col4:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Desfazer", help="Remove o último resultado inserido", use_container_width=True):
        if st.session_state.historico:
            st.session_state.historico.pop()
with col5:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Limpar Histórico", help="Apaga todos os resultados", type="primary", use_container_width=True):
        st.session_state.historico.clear()

st.markdown("---")

st.markdown("### 2. Histórico de Resultados")
# A LINHA ABAIXO FOI ALTERADA PARA EXIBIR OS EMOJIS
historico_str = " ".join([mapear_emojis[r] for r in reversed(st.session_state.historico)])
st.markdown(f"**Mais Recente → Mais Antigo:** {historico_str}")

st.markdown("---")

st.markdown("### 3. Análise e Sugestão")
if st.session_state.historico:
    padrao, sugestao_direta, sugestao_completa = analisar_padrao_dragon_tiger(list(st.session_state.historico))
    st.markdown(f"**Padrão Detectado:** `{padrao}`")
    st.success(f"**{sugestao_direta}**")
    st.info(f"**Explicação:** {sugestao_completa}")
else:
    st.info("O histórico está vazio. Insira resultados para começar a análise.")

# Agradecimento
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("---")
st.write("Desenvolvido para análise de padrões de Dragon Tiger com Streamlit. **Lembre-se:** jogue com responsabilidade.")

