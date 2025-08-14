# 🤖 DevOps Comunidade Bot

Bot do Telegram para apoiar o **Grupo de Estudos DevOps**, com comandos personalizados, formulário de autoavaliação e integração para uso em grupos e no privado.

## 📌 Funcionalidades

- **Comandos customizados**: `/start`, `/form`, `/material`, `/certifications`, `/help`.
- **Formulário de autoavaliação** enviado **apenas no privado**.
- **Mensagens de boas-vindas personalizadas**.
- **Botão de acesso ao formulário no privado** quando usado em grupos.

---

## 🚀 Passo a Passo de Criação

### 1. Criar o Bot no Telegram
1. Abra o Telegram e procure por **[BotFather](https://t.me/BotFather)**.
2. Envie o comando:
   ```
   /newbot
   ```
3. Siga as instruções:
   - Informe um nome para o bot.
   - Informe um **username** único (precisa terminar com `_bot`).
4. Copie o **Token de Acesso** gerado (será usado no código).

---

### 2. Configurar o Bot no BotFather
1. **Ativar em grupos**:
   ```
   /setjoingroups
   ```
   Escolha o seu bot e selecione **Enable**.

2. **Desativar Privacy Mode** (para permitir que o bot leia mensagens em grupos):
   ```
   /setprivacy
   ```
   Escolha o bot e selecione **Disable**.

3. **Definir lista de comandos**:
   ```
   /setcommands
   ```
   Selecione o bot e envie:
   ```
   start - Mensagem de boas-vindas
   form - Formulário de autoavaliação
   material - Links de estudo
   certifications - Trilhas e certificações
   help - Ajuda e contato
   ```

---

### 3. Preparar o Ambiente
O projeto foi desenvolvido em **Python 3.6** usando a biblioteca `python-telegram-bot`.

1. Instale o Python 3.6 ou superior.
2. Crie um ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

---

### 4. Configurar Variáveis de Ambiente
Crie as variáveis de ambiente no terminal ou adicione no `.env`:

```bash
export TELEGRAM_BOT_TOKEN="SEU_TOKEN_AQUI"
export TELEGRAM_BOT_USERNAME="seu_bot_username"
```

---

### 5. Executar o Bot
No terminal:
```bash
python bot.py
```
O bot estará rodando no modo **Polling**.

---

### 6. Adicionar o Bot no Grupo
1. No Telegram, adicione o bot como membro do grupo.
2. Dê permissão para ler mensagens.
3. Agora os comandos como `/start` e `/form` funcionarão.

---

## 📂 Estrutura do Projeto
```
.
├── bot.py                # Código principal do bot
├── requirements.txt      # Dependências do projeto
├── README.md             # Documentação
```

---

## 📋 Fluxo do Formulário
- Em grupos, o `/form` envia um **botão com link** para abrir o formulário no privado.
- No privado, o formulário pergunta:
  - Nome completo
  - Email
  - Autoavaliação (0-5) para Linux, Docker, Kubernetes, CI/CD, etc.

---

## 🔒 Observações de Segurança
- **Nunca** compartilhe seu token público no repositório.
- Use variáveis de ambiente ou arquivos `.env` (adicionados ao `.gitignore`).
- Bots não podem iniciar conversa no privado com usuários — eles precisam clicar no link ou mandar mensagem primeiro.

---

## 📚 Referências
- [Documentação oficial python-telegram-bot](https://docs.python-telegram-bot.org/)
- [BotFather no Telegram](https://t.me/BotFather)
