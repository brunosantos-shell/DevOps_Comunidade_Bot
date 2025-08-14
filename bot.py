import os
import csv
import logging
from datetime import datetime
from pydantic import BaseModel, EmailStr, ValidationError

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
)
from telegram.update import Update

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")

DATA_DIR = "data"
FORMS_CSV = os.path.join(DATA_DIR, "forms.csv")

ALLOWED_GROUP_IDS = set()

SCALE_TEXT = (
    "0 - Nunca usei, 1 - Sei o que é, mas nunca pratiquei, 2 - Já testei, mas não sei configurar sozinho, "
    "3 - Consigo configurar com ajuda de tutoriais, 4 - Consigo configurar e ajudar outros, 5 - Especialista, já implementei do zero"
)

TOPICS = [
    "Linux",
    "Kubernetes On Premise",
    "Docker",
    "Grafana",
    "Prometheus",
    "CI/CD (Geral)",
    "ArgoCD",
    "Git",
    "Jenkins",
    "GitHub Actions",
    "GitLab",
    "Terraform",
    "Amazon ECS",
    "AWS Fargate",
    "AWS CloudFormation",
    "Azure DevOps",
    "ELK",
    "Fluentd",
    "Graylog",
]

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("devops-bot-v13")

os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(FORMS_CSV):
    with open(FORMS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = ["timestamp", "chat_id", "chat_title", "user_id", "username", "name", "email"] + TOPICS
        writer.writerow(header)

def is_allowed_chat(update: Update) -> bool:
    chat = update.effective_chat
    if chat is None:
        return False
    if chat.type in ("group", "supergroup"):
        return (not ALLOWED_GROUP_IDS) or (chat.id in ALLOWED_GROUP_IDS)
    return True

def ensure_bot_username(context: CallbackContext) -> str:
    global BOT_USERNAME
    if not BOT_USERNAME:
        try:
            me = context.bot.get_me()
            BOT_USERNAME = me.username or ""
        except Exception:
            BOT_USERNAME = ""
    return BOT_USERNAME

class FormEntry(BaseModel):
    name: str
    email: EmailStr

ASK_NAME, ASK_EMAIL, ASK_RATING = range(3)

def form_start(update: Update, context: CallbackContext):
    if not is_allowed_chat(update):
        return ConversationHandler.END
    context.user_data.clear()
    context.user_data["ratings"] = {}
    context.user_data["topic_index"] = 0
    update.message.reply_text("Vamos lá! Qual é o *seu nome completo*?", parse_mode="Markdown")
    return ASK_NAME

def form_name(update: Update, context: CallbackContext):
    context.user_data["name"] = update.message.text.strip()
    update.message.reply_text("Perfeito. Qual é o *seu e-mail*?", parse_mode="Markdown")
    return ASK_EMAIL

def form_email(update: Update, context: CallbackContext):
    context.user_data["email"] = update.message.text.strip()
    try:
        FormEntry(name=context.user_data["name"], email=context.user_data["email"])
    except ValidationError as exc:
        update.message.reply_text("Algum dado parece inválido:\n{0}\n\nVamos tentar novamente com /form.".format(exc))
        return ConversationHandler.END
    topic = TOPICS[0]
    context.user_data["last_prompted"] = topic
    context.user_data["topic_index"] = 1
    update.message.reply_text("*{0}*\n{1}\n\nResponda com um número de 0 a 5.".format(topic, SCALE_TEXT), parse_mode="Markdown")
    return ASK_RATING

def _parse_score(text: str):
    t = (text or "").strip()
    if t.isdigit():
        v = int(t)
        if 0 <= v <= 5:
            return v
    return None

def form_rating(update: Update, context: CallbackContext):
    idx = context.user_data.get("topic_index", 0)
    last = context.user_data.get("last_prompted")

    score = _parse_score(update.message.text)
    if score is None:
        update.message.reply_text("Por favor, responda com um número de *0 a 5*.", parse_mode="Markdown")
        return ASK_RATING
    if last:
        context.user_data["ratings"][last] = score

    if idx >= len(TOPICS):
        user = update.effective_user
        chat = update.effective_chat
        row = [
            datetime.utcnow().isoformat(),
            chat.id,
            getattr(chat, "title", ""),
            user.id,
            user.username or "",
            context.user_data.get("name", ""),
            context.user_data.get("email", ""),
        ] + [context.user_data["ratings"].get(t, "") for t in TOPICS]

        with open(FORMS_CSV, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(row)

        update.message.reply_text("✅ Formulário enviado! Obrigado. Usaremos esses dados para os encontros quinzenais. 🚀")
        return ConversationHandler.END

    topic = TOPICS[idx]
    context.user_data["last_prompted"] = topic
    context.user_data["topic_index"] = idx + 1
    update.message.reply_text("*{0}*\n{1}\n\nResponda com um número de 0 a 5.".format(topic, SCALE_TEXT), parse_mode="Markdown")
    return ASK_RATING

def form_cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Formulário cancelado. Pode iniciar novamente com /form.")
    return ConversationHandler.END

def start(update: Update, context: CallbackContext):
    if not is_allowed_chat(update):
        return
    text = """📢 Bem-vindo(a) ao Grupo de Estudos DEVOPS! 🚀

Este é um espaço criado para pessoas que querem evoluir juntas no mundo DevOps.
Aqui, acreditamos que ninguém sabe tudo, mas todos têm algo a ensinar.

Nosso objetivo é compartilhar conhecimento, trocar experiências e construir habilidades práticas em:
Linux, Docker, Kubernetes, CI/CD, Monitoração, Cloud e muito mais.

🔍 Como funciona:

Cada integrante vai preencher um breve formulário para mapearmos o nível de conhecimento em diferentes ferramentas e tecnologias.

Com base nesse mapeamento, criaremos um plano de estudos quinzenal, onde a cada encontro um dos integrantes ministrará um treinamento prático para o grupo.

Nosso foco é mão na massa: aprender praticando, errando juntos e evoluindo em comunidade.

💡 Por que isso é importante?
O mundo DevOps é colaborativo por natureza. Times de alta performance não surgem do nada — eles são construídos com base em aprendizado contínuo, troca de ideias e desafios compartilhados.

✨ Aqui, sua participação importa!
Mesmo que esteja começando agora, sua curiosidade e dedicação farão diferença.
Se já tem experiência, sua visão ajudará outros a crescerem mais rápido.

📆 Primeiro passo:
Preencha o formulário de autoavaliação e venha para nossa primeira reunião.
Vamos juntos transformar curiosidade em conhecimento e conhecimento em resultados.

🚀 Bora codar, automatizar e subir juntos para a nuvem!

Comandos:
/form - formulário de autoavaliação (Nome, E-mail e notas 0-5 por tópico)
/material - links de estudo
/certifications - trilhas e certificações
/help - ajuda e contato

Estamos começando nossa aventura no mundo DevOps! 💻⚙️
A ideia aqui é simples: um ajuda o outro e todo mundo cresce junto.

Cada dúvida que você tiver pode ser a mesma dúvida de outra pessoa.
Cada dica que você souber pode salvar horas de trabalho de alguém.
E cada desafio que aparecer vai ser uma chance de aprender algo novo.

Aqui não tem “eu sei mais” ou “eu sei menos”, tem time unido.
Então bora compartilhar, testar, errar, acertar e, acima de tudo, evoluir juntos.

💬 Pergunte, compartilhe, ajude, provoque ideias… o DevOps é sobre colaboração!"""
    update.message.reply_text(text, disable_web_page_preview=True)

def help_cmd(update: Update, context: CallbackContext):
    if not is_allowed_chat(update): return
    text = (
        "🛠 *Ajuda*\n"
        "/start - boas-vindas\n"
        "/form - formulário (Nome, E-mail e notas 0-5 por tópico)\n"
        "/material - materiais e docs\n"
        "/certifications - certificações sugeridas\n\n"
        "Escala: " + SCALE_TEXT
    )
    update.message.reply_markdown(text)

def material(update: Update, context: CallbackContext):
    if not is_allowed_chat(update): return
    keyboard = [
        [InlineKeyboardButton("📚 Roadmap DevOps", url="https://roadmap.sh/devops")],
        [InlineKeyboardButton("🐳 Docker Docs", url="https://docs.docker.com/")],
        [InlineKeyboardButton("☸️ Kubernetes Docs", url="https://kubernetes.io/docs/")],
        [InlineKeyboardButton("📈 Grafana Docs", url="https://grafana.com/docs/")],
        [InlineKeyboardButton("📊 Prometheus Docs", url="https://prometheus.io/docs/introduction/overview/")],
        [InlineKeyboardButton("🧪 GitHub Actions", url="https://docs.github.com/actions")],
        [InlineKeyboardButton("🧰 GitLab CI", url="https://docs.gitlab.com/ee/ci/")],
        [InlineKeyboardButton("⚙️ Jenkins", url="https://www.jenkins.io/doc/")],
        [InlineKeyboardButton("🌩 Terraform", url="https://developer.hashicorp.com/terraform/docs")],
        [InlineKeyboardButton("🔎 ELK", url="https://www.elastic.co/what-is/elk-stack")],
    ]
    update.message.reply_text("Materiais recomendados:", reply_markup=InlineKeyboardMarkup(keyboard))

def certifications(update: Update, context: CallbackContext):
    if not is_allowed_chat(update): return
    keyboard = [
        [InlineKeyboardButton("AWS Cloud Practitioner", url="https://aws.amazon.com/certification/certified-cloud-practitioner/")],
        [InlineKeyboardButton("CKA (Kubernetes Admin)", url="https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/")],
        [InlineKeyboardButton("Terraform Associate", url="https://www.hashicorp.com/certification/terraform-associate")],
        [InlineKeyboardButton("Azure Fundamentals (AZ-900)", url="https://learn.microsoft.com/certifications/azure-fundamentals/")],
        [InlineKeyboardButton("GitLab Certifications", url="https://about.gitlab.com/learn/certifications/")],
        [InlineKeyboardButton("Grafana Training", url="https://grafana.com/training/")],
    ]
    update.message.reply_text("Trilhas e certificações sugeridas:", reply_markup=InlineKeyboardMarkup(keyboard))

def on_group_text(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.message
    if not chat or chat.type not in ("group", "supergroup"):
        return
    if not is_allowed_chat(update):
        return

    bot_username = ensure_bot_username(context)
    mentioned = False
    if msg.text and bot_username:
        if "@{}".format(bot_username).lower() in msg.text.lower():
            mentioned = True
    if msg.reply_to_message and msg.reply_to_message.from_user and msg.reply_to_message.from_user.id == context.bot.id:
        mentioned = True

    if mentioned:
        msg.reply_text("Oi! Use /help para ver o que eu sei fazer aqui no grupo. 😉")

def main():
    if not TOKEN:
        raise RuntimeError("Defina TELEGRAM_BOT_TOKEN no ambiente")

    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("material", material))
    dp.add_handler(CommandHandler("certifications", certifications))

    conv = ConversationHandler(
        entry_points=[CommandHandler("form", form_start)],
        states={
            ASK_NAME: [MessageHandler(Filters.text & ~Filters.command, form_name)],
            ASK_EMAIL: [MessageHandler(Filters.text & ~Filters.command, form_email)],
            ASK_RATING: [MessageHandler(Filters.text & ~Filters.command, form_rating)],
        },
        fallbacks=[CommandHandler("cancel", form_cancel)],
        allow_reentry=True,
    )
    dp.add_handler(conv)

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, on_group_text))

    logging.info("Bot iniciado em Polling (v13) com /start customizado.")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()