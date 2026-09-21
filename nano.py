#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nano Python para Windows 10 / 11
Editor de texto estilo 'nano' para terminal.
Atalhos:
  Ctrl + S : Salvar
  Ctrl + L : Buscar (digitar e encaminhar para a linha ao teclar Enter)
  Ctrl + X : Sair
"""

import sys
import os
import shutil
import msvcrt
import ctypes
import re

# Habilita cores ANSI / Virtual Terminal Processing no Windows 10 e 11
def habilitar_terminal_virtual():
    try:
        kernel32 = ctypes.windll.kernel32
        h_stdout = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        if kernel32.GetConsoleMode(h_stdout, ctypes.byref(mode)):
            # 0x0004 = ENABLE_VIRTUAL_TERMINAL_PROCESSING
            # 0x0001 = ENABLE_PROCESSED_OUTPUT
            # 0x0002 = ENABLE_WRAP_AT_EOL_OUTPUT
            novo_modo = mode.value | 0x0004 | 0x0001 | 0x0002
            kernel32.SetConsoleMode(h_stdout, novo_modo)
    except Exception:
        pass

# Paleta de Cores ANSI
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[90m"

# Cores requisitadas:
COR_COMENTARIO = "\033[92m"       # Verde vibrante para comentários (# ...)
COR_FUNCAO_DEF = "\033[93;1m"    # Amarelo negrito para nome da função
COR_FUNCAO_CALL = "\033[93m"     # Amarelo para chamadas de função nome(...)
COR_KEYWORD = "\033[96m"         # Ciano para palavras-chave (def, class, if, return, etc)
COR_STRING = "\033[33m"          # Amarelo suave / laranja para strings
COR_NUMERO = "\033[95m"          # Magenta para números

# Barras de status
BARRA_TOPO = "\033[7;1m"         # Invertido
BARRA_STATUS = "\033[7m"         # Invertido
ATALHO_TECLA = "\033[1;47;30m"   # Fundo branco, texto preto
ATALHO_DESC = "\033[0m"

# Expressão regular para destacar sintaxe Python
TOKEN_REGEX = re.compile(
    r'(?P<COMMENT>#.*$)|'
    r'(?P<STRING>"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|'
    r'(?P<DEF_KW>\bdef\b)(?:\s+(?P<DEF_NAME>[a-zA-Z_]\w*))?|'
    r'(?P<FUNC_CALL>\b[a-zA-Z_]\w*)(?=\s*\()|'
    r'(?P<KEYWORD>\b(?:class|return|if|elif|else|for|while|try|except|finally|with|as|import|from|lambda|yield|pass|break|continue|in|is|not|and|or|None|True|False)\b)|'
    r'(?P<NUMBER>\b\d+(?:\.\d+)?\b)'
)

def destacar_linha(linha: str, inicio_col: int, fim_col: int) -> str:
    """Destaca a sintaxe de um pedaço visível da linha de código."""
    if not linha:
        return ""
    tam = len(linha)
    if inicio_col >= tam:
        return ""
    fim_col = min(fim_col, tam)

    tokens = []
    for m in TOKEN_REGEX.finditer(linha):
        gd = m.groupdict()
        if gd.get('COMMENT'):
            tokens.append((m.start('COMMENT'), m.end('COMMENT'), COR_COMENTARIO))
        elif gd.get('STRING'):
            tokens.append((m.start('STRING'), m.end('STRING'), COR_STRING))
        elif gd.get('DEF_KW'):
            tokens.append((m.start('DEF_KW'), m.end('DEF_KW'), COR_KEYWORD))
            if gd.get('DEF_NAME') and m.start('DEF_NAME') != -1:
                tokens.append((m.start('DEF_NAME'), m.end('DEF_NAME'), COR_FUNCAO_DEF))
        elif gd.get('FUNC_CALL'):
            tokens.append((m.start('FUNC_CALL'), m.end('FUNC_CALL'), COR_FUNCAO_CALL))
        elif gd.get('KEYWORD'):
            tokens.append((m.start('KEYWORD'), m.end('KEYWORD'), COR_KEYWORD))
        elif gd.get('NUMBER'):
            tokens.append((m.start('NUMBER'), m.end('NUMBER'), COR_NUMERO))

    # Realiza o corte com segurança mantendo as cores intactas
    fatias = []
    cursor = inicio_col

    for t_ini, t_fim, cor in tokens:
        if t_fim <= inicio_col:
            continue
        if t_ini >= fim_col:
            break

        if cursor < t_ini:
            gap_fim = min(t_ini, fim_col)
            fatias.append((cursor, gap_fim, None))
            cursor = gap_fim

        ov_ini = max(t_ini, cursor)
        ov_fim = min(t_fim, fim_col)
        if ov_ini < ov_fim:
            fatias.append((ov_ini, ov_fim, cor))
            cursor = ov_fim

    if cursor < fim_col:
        fatias.append((cursor, fim_col, None))

    resultado = []
    for s_ini, s_fim, cor in fatias:
        pedaço = linha[s_ini:s_fim]
        if cor:
            resultado.append(f"{cor}{pedaço}{RESET}")
        else:
            resultado.append(pedaço)

    return "".join(resultado)

class NanoEditor:
    def __init__(self, caminho_arquivo: str = None):
        self.caminho = caminho_arquivo
        self.linhas = [""]
        self.modificado = False
        self.cy = 0       # Linha do cursor (0-indexada)
        self.cx = 0       # Coluna do cursor (0-indexada)
        self.scroll_y = 0 # Rolagem vertical
        self.scroll_x = 0 # Rolagem horizontal
        self.status_msg = ""
        self.ultimo_termo_busca = ""
        self.carregar_arquivo()

    def carregar_arquivo(self):
        if self.caminho and os.path.exists(self.caminho):
            try:
                with open(self.caminho, 'r', encoding='utf-8', errors='replace') as f:
                    conteudo = f.read().splitlines()
                self.linhas = conteudo if conteudo else [""]
                self.status_msg = f"[ Lido {len(self.linhas)} linhas de '{os.path.basename(self.caminho)}' ]"
            except Exception as e:
                self.status_msg = f"[ Erro ao ler arquivo: {e} ]"
                self.linhas = [""]
        else:
            if self.caminho:
                self.status_msg = f"[ Novo arquivo: '{os.path.basename(self.caminho)}' ]"
            else:
                self.status_msg = "[ Novo arquivo ]"

    def salvar_arquivo(self, novo_nome: str = None):
        if novo_nome:
            self.caminho = novo_nome.strip()

        if not self.caminho:
            nome = self.perguntar("Nome do arquivo para salvar: ")
            if not nome:
                self.status_msg = "[ Salvamento cancelado ]"
                return False
            self.caminho = nome.strip()

        try:
            with open(self.caminho, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.linhas) + "\n")
            self.modificado = False
            self.status_msg = f"[ Gravado {len(self.linhas)} linhas em '{os.path.basename(self.caminho)}' ]"
            return True
        except Exception as e:
            self.status_msg = f"[ Erro ao salvar: {e} ]"
            return False

    def obter_dimensoes(self):
        ts = shutil.get_terminal_size(fallback=(80, 25))
        return ts.lines, ts.columns

    def perguntar(self, prompt: str) -> str:
        """Exibe um prompt de texto na linha de status e lê a resposta do usuário."""
        linhas, colunas = self.obter_dimensoes()
        linha_prompt = linhas - 1
        resposta = []

        while True:
            # Renderiza linha de prompt
            txt = prompt + "".join(resposta)
            txt_formatado = f"\033[{linha_prompt};1H\033[7m{txt:<{colunas}}\033[0m"
            pos_cursor = len(prompt) + len(resposta) + 1
            sys.stdout.write(txt_formatado + f"\033[{linha_prompt};{pos_cursor}H\033[?25h")
            sys.stdout.flush()

            ch = msvcrt.getwch()
            if ch in ('\r', '\n'):
                break
            elif ch == '\x1b':  # ESC cancela
                return None
            elif ch == '\x08':  # Backspace
                if resposta:
                    resposta.pop()
            elif ch in ('\x00', '\xe0'):
                msvcrt.getwch()  # ignora teclas de função
            elif ch.isprintable():
                resposta.append(ch)

        return "".join(resposta)

    def ir_para_linha(self, num_linha: int):
        """Move o cursor para a linha especificada (1-indexada)."""
        total = len(self.linhas)
        if num_linha < 1:
            num_linha = 1
        elif num_linha > total:
            num_linha = total

        self.cy = num_linha - 1
        self.cx = 0

        linhas_term, _ = self.obter_dimensoes()
        altura_edicao = max(1, linhas_term - 3)
        self.scroll_y = max(0, self.cy - (altura_edicao // 2))
        self.scroll_x = 0
        self.status_msg = f"[ Linha {self.cy + 1}/{total} ]"

    def buscar_texto(self):
        """Busca texto ou linha (Ctrl + L). Pressionar Enter vai para a ocorrência."""
        prompt = f"Buscar [{self.ultimo_termo_busca}]: " if self.ultimo_termo_busca else "Buscar: "
        termo = self.perguntar(prompt)

        # Cancelado com ESC
        if termo is None:
            self.status_msg = "[ Busca cancelada ]"
            return

        termo = termo.strip()
        # Se deu Enter vazio, repete o termo anterior
        if not termo:
            if self.ultimo_termo_busca:
                termo = self.ultimo_termo_busca
            else:
                self.status_msg = "[ Digite algo para buscar ]"
                return

        self.ultimo_termo_busca = termo

        # Suporte a ir direto à linha: :42 ou número de linha se começar com ':'
        if termo.startswith(":") and termo[1:].strip().isdigit():
            self.ir_para_linha(int(termo[1:].strip()))
            return

        termo_lower = termo.lower()
        total_linhas = len(self.linhas)
        match_cy = None
        match_cx = None
        envolveu = False

        # 1. Procura na linha atual após a posição atual do cursor
        linha_atual = self.linhas[self.cy]
        pos = linha_atual.lower().find(termo_lower, self.cx + 1)
        if pos != -1:
            match_cy = self.cy
            match_cx = pos
        else:
            # 2. Procura nas linhas seguintes até o final do arquivo
            for idx in range(self.cy + 1, total_linhas):
                pos = self.linhas[idx].lower().find(termo_lower)
                if pos != -1:
                    match_cy = idx
                    match_cx = pos
                    break

        # 3. Se não encontrou até o final, recomeça do topo do arquivo (wrap)
        if match_cy is None:
            for idx in range(0, self.cy):
                pos = self.linhas[idx].lower().find(termo_lower)
                if pos != -1:
                    match_cy = idx
                    match_cx = pos
                    envolveu = True
                    break

            # 4. Procura na linha atual do início até a posição do cursor
            if match_cy is None:
                pos = linha_atual.lower().find(termo_lower)
                if pos != -1 and pos <= self.cx:
                    match_cy = self.cy
                    match_cx = pos
                    envolveu = True

        if match_cy is not None:
            self.cy = match_cy
            self.cx = match_cx
            linhas_term, cols_term = self.obter_dimensoes()
            altura_edicao = max(1, linhas_term - 3)

            # Centraliza a visualização verticalmente na ocorrência
            if self.cy < self.scroll_y or self.cy >= self.scroll_y + altura_edicao:
                self.scroll_y = max(0, self.cy - (altura_edicao // 2))

            # Ajusta rolagem horizontal se necessário
            largura_num = max(3, len(str(total_linhas)))
            largura_calha = largura_num + 3
            largura_texto = max(10, cols_term - largura_calha)
            if self.cx < self.scroll_x or self.cx >= self.scroll_x + largura_texto:
                self.scroll_x = max(0, self.cx - (largura_texto // 4))

            if envolveu:
                self.status_msg = f"[ Busca recomeçou do início: Linha {self.cy + 1}, Col {self.cx + 1} ]"
            else:
                self.status_msg = f"[ Encontrado na linha {self.cy + 1}, Col {self.cx + 1} ]"
        else:
            # Se não achou texto mas o usuário digitou só números, vai para essa linha
            if termo.isdigit() and 1 <= int(termo) <= total_linhas:
                self.ir_para_linha(int(termo))
            else:
                self.status_msg = f"[ '{termo}' não encontrado ]"

    def desenhar(self):
        linhas_term, cols_term = self.obter_dimensoes()
        altura_edicao = max(1, linhas_term - 3)
        total_linhas = len(self.linhas)

        # Ajusta rolagem vertical
        if self.cy < self.scroll_y:
            self.scroll_y = self.cy
        elif self.cy >= self.scroll_y + altura_edicao:
            self.scroll_y = self.cy - altura_edicao + 1

        # Largura da calha de números de linha
        largura_num = max(3, len(str(total_linhas)))
        largura_calha = largura_num + 3  # "  1 | "
        largura_texto = max(10, cols_term - largura_calha)

        # Ajusta rolagem horizontal
        if self.cx < self.scroll_x:
            self.scroll_x = self.cx
        elif self.cx >= self.scroll_x + largura_texto:
            self.scroll_x = self.cx - largura_texto + 1

        buffer = []
        buffer.append("\033[?25l")  # Oculta cursor temporariamente durante a renderização
        buffer.append("\033[H")     # Move para o topo esquerdo

        # 1. Barra de Título Superior
        nome_exibicao = os.path.basename(self.caminho) if self.caminho else "Sem Título"
        status_mod = " [Modificado]" if self.modificado else ""
        titulo = f" Nano Python 1.0  |  Arquivo: {nome_exibicao}{status_mod}"
        if len(titulo) > cols_term:
            titulo = titulo[:cols_term]
        buffer.append(f"{BARRA_TOPO}{titulo:<{cols_term}}{RESET}\r\n")

        # 2. Área de Edição com Números de Linha
        for i in range(altura_edicao):
            idx_linha = self.scroll_y + i
            if idx_linha < total_linhas:
                num_str = f"{idx_linha + 1:>{largura_num}}"
                calha = f"{DIM}{num_str} |{RESET} "

                linha_conteudo = self.linhas[idx_linha]
                texto_colorido = destacar_linha(linha_conteudo, self.scroll_x, self.scroll_x + largura_texto)
                
                # Preenche o resto da linha para limpar qualquer resíduo
                buffer.append(f"{calha}{texto_colorido}\033[K\r\n")
            else:
                # Linha após o fim do arquivo
                calha = f"{DIM}{'~':>{largura_num}} |{RESET} "
                buffer.append(f"{calha}\033[K\r\n")

        # 3. Linha de Mensagem / Status
        msg = self.status_msg
        if len(msg) > cols_term:
            msg = msg[:cols_term]
        buffer.append(f"\033[7m{msg:<{cols_term}}{RESET}\r\n")

        # 4. Barra de Atalhos Inferior (Estilo Nano)
        atalhos = (
            f"{ATALHO_TECLA} ^S {ATALHO_DESC} Salvar  "
            f"{ATALHO_TECLA} ^L {ATALHO_DESC} Buscar  "
            f"{ATALHO_TECLA} ^X {ATALHO_DESC} Sair  "
            f"{DIM}|{RESET} Lin {self.cy + 1}/{total_linhas}, Col {self.cx + 1} "
        )
        buffer.append(f"{atalhos}\033[K")

        # Posiciona o cursor físico na posição correta da tela
        tela_y = (self.cy - self.scroll_y) + 2  # Linha 1 é o cabeçalho
        tela_x = 1 + largura_calha + (self.cx - self.scroll_x)
        buffer.append(f"\033[{tela_y};{tela_x}H")
        buffer.append("\033[?25h")  # Mostra o cursor

        sys.stdout.write("".join(buffer))
        sys.stdout.flush()

    def processar_tecla(self) -> bool:
        """Lê e processa uma tecla. Retorna False se o editor deve fechar."""
        ch = msvcrt.getwch()

        # Teclas especiais estendidas (Setas, Delete, Home, End, etc.)
        if ch in ('\x00', '\xe0'):
            tecla_esp = msvcrt.getwch()
            self.tratar_tecla_especial(tecla_esp)
            return True

        # Ctrl + S: Salvar
        if ch == '\x13':
            self.salvar_arquivo()
            return True

        # Ctrl + L (e compatibilidade com Ctrl + W / Ctrl + F): Buscar
        if ch in ('\x0c', '\x17', '\x06'):
            self.buscar_texto()
            return True

        # Ctrl + G: Ir diretamente para o número da linha
        if ch == '\x07':
            resp = self.perguntar("Ir para a linha: ")
            if resp and resp.strip().isdigit():
                self.ir_para_linha(int(resp.strip()))
            elif resp is not None:
                self.status_msg = "[ Linha inválida ]"
            else:
                self.status_msg = "[ Cancelado ]"
            return True

        # Ctrl + X: Sair
        if ch == '\x18':
            if self.modificado:
                resp = self.perguntar("Salvar alterações antes de sair? (S)im / (N)ão / (C)ancela: ").strip().lower()
                if resp in ('s', 'sim', 'y', 'yes'):
                    if self.salvar_arquivo():
                        return False
                    return True
                elif resp in ('n', 'nao', 'não', 'no'):
                    return False
                else:
                    self.status_msg = "[ Cancelado ]"
                    return True
            else:
                return False

        # Enter
        if ch in ('\r', '\n'):
            linha_atual = self.linhas[self.cy]
            esquerda = linha_atual[:self.cx]
            direita = linha_atual[self.cx:]

            # Auto-indentação simples
            espacos = len(esquerda) - len(esquerda.lstrip(' '))
            indent = " " * espacos
            if esquerda.rstrip().endswith(':'):
                indent += "    "

            self.linhas[self.cy] = esquerda
            self.linhas.insert(self.cy + 1, indent + direita)
            self.cy += 1
            self.cx = len(indent)
            self.modificado = True
            self.status_msg = ""
            return True

        # Backspace
        if ch == '\x08':
            if self.cx > 0:
                linha = self.linhas[self.cy]
                # Apaga 4 espaços de uma vez se for indentação
                if self.cx >= 4 and linha[:self.cx].endswith("    ") and linha[:self.cx].strip() == "":
                    self.linhas[self.cy] = linha[:self.cx - 4] + linha[self.cx:]
                    self.cx -= 4
                else:
                    self.linhas[self.cy] = linha[:self.cx - 1] + linha[self.cx:]
                    self.cx -= 1
                self.modificado = True
            elif self.cy > 0:
                # Junta com a linha anterior
                len_anterior = len(self.linhas[self.cy - 1])
                self.linhas[self.cy - 1] += self.linhas[self.cy]
                del self.linhas[self.cy]
                self.cy -= 1
                self.cx = len_anterior
                self.modificado = True
            self.status_msg = ""
            return True

        # Tab (Insere 4 espaços)
        if ch == '\t':
            linha = self.linhas[self.cy]
            self.linhas[self.cy] = linha[:self.cx] + "    " + linha[self.cx:]
            self.cx += 4
            self.modificado = True
            self.status_msg = ""
            return True

        # Caracteres normais digitáveis
        if ch.isprintable():
            linha = self.linhas[self.cy]
            self.linhas[self.cy] = linha[:self.cx] + ch + linha[self.cx:]
            self.cx += 1
            self.modificado = True
            self.status_msg = ""
            return True

        return True

    def tratar_tecla_especial(self, codigo: str):
        altura_edicao = max(1, self.obter_dimensoes()[0] - 3)

        if codigo == 'H':    # Seta para CIMA
            if self.cy > 0:
                self.cy -= 1
                self.cx = min(self.cx, len(self.linhas[self.cy]))
        elif codigo == 'P':  # Seta para BAIXO
            if self.cy < len(self.linhas) - 1:
                self.cy += 1
                self.cx = min(self.cx, len(self.linhas[self.cy]))
        elif codigo == 'K':  # Seta para ESQUERDA
            if self.cx > 0:
                self.cx -= 1
            elif self.cy > 0:
                self.cy -= 1
                self.cx = len(self.linhas[self.cy])
        elif codigo == 'M':  # Seta para DIREITA
            if self.cx < len(self.linhas[self.cy]):
                self.cx += 1
            elif self.cy < len(self.linhas) - 1:
                self.cy += 1
                self.cx = 0
        elif codigo == 'S':  # Tecla DELETE
            linha = self.linhas[self.cy]
            if self.cx < len(linha):
                self.linhas[self.cy] = linha[:self.cx] + linha[self.cx + 1:]
                self.modificado = True
            elif self.cy < len(self.linhas) - 1:
                # Junta com a linha de baixo
                self.linhas[self.cy] += self.linhas[self.cy + 1]
                del self.linhas[self.cy + 1]
                self.modificado = True
        elif codigo == 'G':  # HOME
            self.cx = 0
        elif codigo == 'O':  # END
            self.cx = len(self.linhas[self.cy])
        elif codigo == 'I':  # PAGE UP
            self.cy = max(0, self.cy - altura_edicao)
            self.cx = min(self.cx, len(self.linhas[self.cy]))
        elif codigo == 'Q':  # PAGE DOWN
            self.cy = min(len(self.linhas) - 1, self.cy + altura_edicao)
            self.cx = min(self.cx, len(self.linhas[self.cy]))

    def executar(self):
        habilitar_terminal_virtual()
        # Salva o buffer da tela atual do terminal e limpa
        sys.stdout.write("\033[?1049h\033[2J")
        sys.stdout.flush()

        try:
            while True:
                self.desenhar()
                if not self.processar_tecla():
                    break
        finally:
            # Restaura tela anterior do terminal e o cursor
            sys.stdout.write("\033[?1049l\033[?25h")
            sys.stdout.flush()

def main():
    arquivo = sys.argv[1] if len(sys.argv) > 1 else None
    editor = NanoEditor(arquivo)
    editor.executar()

if __name__ == "__main__":
    main()
