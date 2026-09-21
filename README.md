# 📝 Nano for Windows (nano-win)

Um editor de texto leve para terminal no **Windows 10 e 11**, inspirado no clássico **GNU nano**.

Possui numeração de linhas, atalhos intuitivos (<kbd>Ctrl</kbd> + <kbd>S</kbd> para salvar e <kbd>Ctrl</kbd> + <kbd>X</kbd> para sair) e **colorização de sintaxe com comentários em verde e funções em destaque**.

Disponível tanto em script **Python puro** quanto em **executável (.exe) standalone** que não necessita de Python instalado na máquina.

---

## ✨ Recursos

- **⚡ Atalhos Rápidos:**
  - `Ctrl + S` — Salva o arquivo atual (se não tiver nome, solicita no rodapé).
  - `Ctrl + X` — Sai do editor com diálogo de confirmação caso haja alterações não salvas (`Sim / Não / Cancelar`).
- **🔢 Régua com Numeração de Linhas:** Coluna à esquerda que se ajusta automaticamente ao tamanho do documento.
- **🎨 Destaque de Sintaxe Inteligente:**
  - 🟢 **Comentários (`# ...`):** Verde vibrante.
  - 🟡 **Funções:** Destaque em amarelo negrito (`def nome_funcao`) e amarelo em chamadas de função (`funcao()`).
  - 🔵 **Palavras-chave:** Ciano (`class`, `return`, `if`, `for`, `import`, etc.).
  - 🟠 **Strings e Números:** Tons suaves e legíveis.
- **🖥️ 100% Nativo para Windows:** Utiliza sequências ANSI/VT100 nativas do Windows 10/11 sem depender de bibliotecas externas pesadas.
- **🧹 Terminal Limpo:** Utiliza tela alternativa do terminal (`Alternate Screen Buffer`), restaurando exatamente o estado anterior do seu terminal ao sair.

---

## ⌨️ Comandos e Navegação

| Tecla | Ação |
| :--- | :--- |
| <kbd>Ctrl</kbd> + <kbd>S</kbd> | Salvar arquivo |
| <kbd>Ctrl</kbd> + <kbd>X</kbd> | Sair do editor |
| <kbd>Setas</kbd> (↑ ↓ ← →) | Movimenta o cursor |
| <kbd>Home</kbd> / <kbd>End</kbd> | Início / Fim da linha atual |
| <kbd>Page Up</kbd> / <kbd>Page Down</kbd> | Rola tela para cima / baixo |
| <kbd>Tab</kbd> | Insere 4 espaços de indentação |
| <kbd>Enter</kbd> | Nova linha com auto-indentação |
| <kbd>Backspace</kbd> / <kbd>Delete</kbd> | Apaga caracteres ou mescla linhas |

---

## 🚀 Como Instalar e Configurar

Você pode utilizar o `nano` de duas maneiras:

### Opção 1: Usando o Executável Standalone (`nano.exe`) — Recomendado

Com o arquivo `nano.exe`, você não precisa ter o Python instalado na máquina.

#### 1. Escolha uma pasta para o executável
Crie uma pasta para suas ferramentas (por exemplo `C:\Ferramentas`) e coloque o `nano.exe` dentro dela:
```powershell
New-Item -ItemType Directory -Path "C:\Ferramentas" -Force
Copy-Item "nano.exe" -Destination "C:\Ferramentas\nano.exe"
```

#### 2. Adicione a pasta às Variáveis de Ambiente (`PATH`)

##### Via PowerShell (Rápido):
Abra o PowerShell e execute o comando abaixo para adicionar a pasta ao seu `PATH` de usuário:
```powershell
[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Ferramentas",
    "User"
)
```

##### Ou via Interface Gráfica do Windows:
1. Pressione <kbd>Windows</kbd> + <kbd>R</kbd>, digite `sysdm.cpl` e dê **Enter**.
2. Vá na aba **Avançado** e clique em **Variáveis de Ambiente...**.
3. Na seção superior (*Variáveis de usuário*), selecione **Path** e clique em **Editar...**.
4. Clique em **Novo** e digite o caminho da pasta (ex: `C:\Ferramentas`).
5. Clique em **OK** em todas as janelas.

> **Dica:** Reinicie ou abra uma nova janela do terminal (CMD/PowerShell) após alterar as variáveis de ambiente.

---

### Opção 2: Executando a partir do Script Python (`nano.py`)

Se você tem o Python 3.10+ instalado:

```powershell
python nano.py arquivo.py
```

#### Para compilar seu próprio `.exe`:
Se quiser compilar por conta própria a partir do código fonte:
```powershell
pip install pyinstaller
pyinstaller --onefile --console --name nano nano.py
```
O executável compilado estará dentro da pasta `dist/nano.exe`.

---

## 💻 Como Usar

Abra o **PowerShell**, **Prompt de Comando (CMD)** ou **Windows Terminal** em qualquer pasta e digite:

Criar ou abrir um arquivo existente:
```powershell
nano script.py
```

Abrir o editor vazio sem título:
```powershell
nano
```

Editar arquivos de configuração:
```powershell
nano config.json
nano .env
```

---

## 📄 Licença

Distribuído sob a licença MIT. Sinta-se livre para usar, modificar e distribuir.
