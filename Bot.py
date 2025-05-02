from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import time

# Configurações do navegador
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Roda sem abrir a janela

# Inicia o navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Acessa a página
url = 'https://liquipedia.net/counterstrike/FURIA'
driver.get(url)
time.sleep(0.2)

#Dá um "hello" para o usuário
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("😎 Olá torcedor FURIOSO 😎\n"
                                    "\n"
                                    "Eu sou o BOT da FURIA e irei ser o seu guru de informações do nosso time\n"
                                    "\n"
                                    "Para começarmos digite um dos seguintes comandos: 🫡")

    await comandos(update, context)

# Pega as informações do próximo jogo
async def proximojogo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        caixaProximoJogoExiste = driver.find_element(By.XPATH, "//div[@class='infobox-header']") #Procura no codigo HTML se existe uma próxima partida

        if caixaProximoJogoExiste:
            oponente = driver.find_element(By.XPATH, "//td[contains(@class, 'team-right')]//span[contains(@class, 'team-template-text')]/a")
            tempoRestante = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'timer-object-countdown-time')]"))) #Espera até 10 segundos para encontrar o elemento dinâmico (contagem regressiva)
            torneio = driver.find_element(By.XPATH, "//div[contains(@class, 'tournament-text-flex')]/a")

            await update.message.reply_text("🎮💪 PRÓXIMA PARTIDA: 💪🎮\n"
                                            "\n"
                                            f"🖤🤍 FURIA 🆚 {oponente.text} 🔥🔥🔥\n"
                                            f"⏳ Faltam {tempoRestante.text} para o ínicio da partida\n"
                                            f"🏆 A partida é valida pelo {torneio.text}")

    except NoSuchElementException: #Caso não encontre uma caixa com a próxima partida é lançada esta excessão
        await update.message.reply_text("😢 Não há uma próxima partida marcada para a FURIA 😢")

#Traz informações sobre a lineup ativa da quipe
async def lineup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lineDoTime = driver.find_elements(By.CLASS_NAME, "Player")[:5] #Pega os primeiros 5 jogadores da página (pool ativo de players)
    mensagem = ""

    for jogadores in lineDoTime:
        nick = jogadores.find_element(By.XPATH, ".//td[@class='ID']//a") #Filtra o apelido do jogador
        nome = jogadores.find_element(By.XPATH, ".//td[(@class='Name')]//div[(@class='LargeStuff')]") #Filtra o nome do jogador
        mensagem += f"🪖 {nick.text} - {nome.text}\n"

    coach = driver.find_element(By.XPATH, "//tr[(@class='Player coach roster-coach')]") #Encontra o coach ativo do time
    coachNick = coach.find_element(By.XPATH, ".//td[@class='ID']//a")
    coachNome = coach.find_element(By.XPATH, ".//td[(@class='Name')]//div[(@class='LargeStuff')]")
    mensagem += f"✒️ {coachNick.text} - {coachNome.text} (COACH)"

    await update.message.reply_text(mensagem)

#Lista os comandos para o usuário
async def comandos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("LISTA DE COMANDOS\n"
                                    "\n"
                                    "/start - informações sobre o BOT\n"
                                    "/comandos ou /help - lista os comandos do BOT\n"
                                    "/lineup - informações sobre a line ativa\n"
                                    "/proximojogo - informações sobre o proximo jogo\n"
                                    "/proximocamp - informações sobre o proximo campeonato\n"
                                    "/ultimosresultados - resultados das últimas 5 partidas\n"
                                    "/historico - resultado geral da equipe\n"
                                    "/paginas - redes sociais da FURIA\n"
                                    "/grupo - grupo de fans")

#Traz informações sobre o proximo campeonato
async def proximocamp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        caixaProximoCampExiste = driver.find_elements(By.XPATH, "//div[@class='infobox-header wiki-backgroundcolor-light']")[1] #Procura no codigo HTML se existe um próximo campeonato

        if caixaProximoCampExiste:
            torneio = driver.find_elements(By.XPATH, "//td[(@class='versus')]//a")[1] #Index fixado pois o [0] retorna nulo
            dataTorneio = driver.find_element(By.XPATH, "//div[(@class='text-nowrap')]//div")
            await update.message.reply_text("🏆💪 PRÓXIMO CAMPEONATO: 💪🏆\n"
                                            "\n"
                                            f"🏆 Próximo Campeonato: {torneio.text}\n"
                                            f"📅 Duração: {dataTorneio.text}")

    except NoSuchElementException: #Caso não encontre uma caixa com o próximo campeonato é lançada esta excessão
        await update.message.reply_text("😢 Não há um próximo campeonato no nosso calendário 😢")

#Mostra o resultado dos últimos 5 jogos
async def ultimosresultados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    urlMatch = 'https://liquipedia.net/counterstrike/FURIA/Matches'
    driver.get(urlMatch)
    time.sleep(0.2)
    mensagem = ""

    ultimasPartidas = driver.find_elements(By.XPATH, "//table[(@class='wikitable wikitable-striped sortable jquery-tablesorter')]//tbody//tr")[:5] #Encontra as 5 ultimas partidas

    for partida in ultimasPartidas:
        resultado = partida.find_element(By.XPATH, ".//td[(@class='match-table-score')]")
        oponente = partida.find_element(By.XPATH, ".//td[(@style='text-align:left')]//span[(@class='name')]")
        mensagem+= f"{resultado.text} 🆚 {oponente.text}\n"

    await update.message.reply_text(f"{mensagem}")

#Traz um histórico geral da FURIA
async def historico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    urlMatch = "https://liquipedia.net/counterstrike/FURIA/Matches"
    driver.get(urlMatch)
    time.sleep(0.2)

    historicoGeral = driver.find_element(By.XPATH, "(//div[@style='font-weight:bold']/following-sibling::div)")

    #Faz a divisão do texto para pegar apenas a informação necessária
    vitorias = historicoGeral.text.split("W")[0]
    empates = historicoGeral.text.split(": ")[1].split("D")[0]
    derrotas = historicoGeral.text.split("D : ")[1].split("L")[0]
    porcentagem = historicoGeral.text.split("(")[1].split(")")[0]

    await update.message.reply_text(f"📊 HISTÓRICO GERAL \n"
                                    f"\n"
                                    f"✅ VITÓRIAS - {vitorias}\n"
                                    f"🤝 EMPATES - {empates}\n"
                                    f"❌ DERROTAS - {derrotas}\n"
                                    f"📈 APROVEITAMENTO - {porcentagem}")

#Lista as páginas socias da FURIA
async def paginas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛍️ LOJA OFICIAL: https://www.furia.gg\n"
                                    "📷 INSTAGRAM: https://www.instagram.com/furiagg/\n"
                                    "🎵 TIKTOK: https://www.tiktok.com/@furiagg\n"
                                    "🕊️ X: https://x.com/furia\n"
                                    "📘 FACEBOOK: https://www.facebook.com/furiagg\n"
                                    "▶️ YOUTUBE: https://www.youtube.com/@FURIAggCS")

#Envia o link para o grupo de comunicação entre os fãs (FANZONE)
async def grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("LINK PARA NOSSA FANZONE: \n"
                                    "🖤🤍 https://t.me/+VBue7IQoT-A4NTlh 🤍🖤\n"
                                    "EMPURRA!!!")

if __name__ == '__main__':
    app = ApplicationBuilder().token("7863127163:AAE85-rsxyiZbrcrnaJX_44KUO6TGZTcDAE").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("proximojogo", proximojogo))
    app.add_handler(CommandHandler("lineup", lineup))
    app.add_handler(CommandHandler("comandos", comandos))
    app.add_handler(CommandHandler("help", comandos))
    app.add_handler(CommandHandler("proximocamp", proximocamp))
    app.add_handler(CommandHandler("ultimosresultados", ultimosresultados))
    app.add_handler(CommandHandler("historico", historico))
    app.add_handler(CommandHandler("paginas", paginas))
    app.add_handler(CommandHandler("grupo", grupo))


    print("Bot rodando...")
    app.run_polling()

# Fecha o navegador
driver.quit()
