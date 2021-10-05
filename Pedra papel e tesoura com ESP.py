import urllib.request
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.models import load_model
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os.path
from time import sleep
from random import randint
from mutagen.mp3 import MP3

# Função para ouvir e reconhecer a fala
def ouvir_microfone(tempo):
    # Habilita o microfone do usuário
    microfone = sr.Recognizer()
    # usando o microfone
    with sr.Microphone() as source:
        # Chama um algoritmo de reducao de ruidos no som
        microfone.adjust_for_ambient_noise(source, duration=2)
        # Frase para o usuario dizer algo
        print("Diga alguma coisa: ")
        # Armazena o que foi dito numa variavel
        audio = microfone.record(source, duration=tempo)

    try:
        # Passa a variável para o algoritmo reconhecedor de padroes
        frase = microfone.recognize_google(audio, language='pt-BR')
        # Retorna a frase pronunciada
        print("Você disse: " + frase)
    # Se nao reconheceu o padrao de fala, exibe a mensagem
    except:
        print("Não entendi")
        frase = ''
    return frase

#Funcao responsavel por falar
def cria_audio(texto, nome, condicao):
    if os.path.isfile(nome) == True:
            playsound(nome, condicao)
    else:
        tts = gTTS(text=texto,lang='pt-br')
        #Salva o arquivo de audio
        tts.save(nome)
        #Da play ao audio
        playsound(nome, condicao)

def reconhecimento_de_imagem():
    global url, urlPisca, urlFlash, listaDosNomes, mpMao, maos, mpDesenho, saiuDeteccao, umaVezEntrou, umaVezSaiu, saiuNoComando, PPT
    imgResp = urllib.request.urlopen(url)
    imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
    img = cv2.imdecode(imgNp, -1)
    x, y, c = img.shape

    frameBGR = cv2.flip(img, 1)
    frameRGB = cv2.cvtColor(frameBGR, cv2.COLOR_BGR2RGB)

    resultado = maos.process(frameRGB)
    nomeDoGesto = ''

    # Checa se alguma mão foi detectada ou não
    if resultado.multi_hand_landmarks:
        # aqui me da um dicionario de landmark {}, landmark são as marcacoes
        saiuDeteccao = True
        umaVezSaiu = True
        if saiuDeteccao == True and umaVezEntrou == False:
            mao_reconhecida(saiuDeteccao)
            umaVezEntrou = True
        marcacoes = []
        urllib.request.urlopen(urlFlash)
        for maosCoordenadas in resultado.multi_hand_landmarks:
            # aqui vai me dar as coordenadas dentro do dicionário landmark
            for coordenadas in maosCoordenadas.landmark:
                # multiplicamos por x e y dea imagem pq as coordenadas vem normalizadas
                coordenadax = int(coordenadas.x * x)
                coordenaday = int(coordenadas.y * y)
                #isso faz desenhar os circulos na coordenadas da mão
                mpDesenho.draw_landmarks(frameBGR, maosCoordenadas, mpMao.HAND_CONNECTIONS)
                marcacoes.append([coordenadax,coordenaday])

            prediction = modelo.predict([marcacoes])
            maiorNumero = np.argmax(prediction)
            nomeDoGesto = listaDosNomes[maiorNumero]
            cv2.putText(frameBGR, nomeDoGesto, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            if PPT == True:
                pedra_papel_tesoura(saiuDeteccao)
    else:
        saiuDeteccao = False
        if saiuDeteccao == False and umaVezSaiu == True:
            mao_reconhecida(saiuDeteccao)
            umaVezSaiu = False
            umaVezEntrou = False

    if cv2.waitKey(1) == ord('q'):
        pass

def comando_chamar(url):
    global comando, condicao
    frase = ouvir_microfone(2)
    if frase == 'ativar robô' or frase == 'ativar':
        cria_audio('Olá, estou ligado. Por favor, me dê um comando.','greetings.mp3', False)
        urllib.request.urlopen(urlFlash)
        urllib.request.urlopen(urlAtivar)
        fala('greetings.mp3', 2)
        condicao = True
        comando = True
    else:
        comando_chamar(url)

def fala(nome, menos):
    sleep(int(MP3(nome).info.length)-menos)

def comando_robo(reconhecimento, tempoMic):
    global urlPisca, comando, saiuDeteccao, PPT, jogadas
    algumaResposta = False
    if PPT == True:
        checar_mao(saiuDeteccao)
    frase = ouvir_microfone(tempoMic)
    if reconhecimento == False and (frase == 'pedra papel e tesoura' or frase == 'pedra papel tesoura' or frase == 'jogar' or frase == 'Jogar'):
        cria_audio('Ok, vamos jogar pedra, papel e tesoura. Por favor, coloque sua mão próxima a câmera para que eu possa detecta-la', 'deteccao.mp3', False)
        fala('deteccao.mp3', 4)
        algumaResposta = True
        comando = False
        PPT = True
    if reconhecimento == True and (frase == 'sim' or frase == 'estou pronto' or frase == 'tô pronto'):
        cria_audio('Ok! Você deve fazer sua jogada com a palma da mão virada para a câmera. Vamos lá', 'explanation.mp3', True)
        cria_audio('Pedra... Papel... e... TESOURA!', 'ppt.mp3', True)
        sleep(1)
        jogadaPlayer = jogada_player()
        while jogadaPlayer == None :
            jogadaPlayer = jogada_player()
        print(jogadaPlayer)
        jogadaMaquina = jogadas[randint(0,2)]
        print(jogadaMaquina)
        if jogadaMaquina == 'Pedra':
            urllib.request.urlopen(urlPedra)
        elif jogadaMaquina == 'Tesoura':
            urllib.request.urlopen(urlTesoura)
        elif jogadaMaquina == 'Papel':
            urllib.request.urlopen(urlPedra)
            urllib.request.urlopen(urlPapel)
        algumaResposta = True
        PPT = False
        jogo(jogadaMaquina, jogadaPlayer)
    if algumaResposta == False:
        cria_audio('Não entendi o comando, repita.', 'naoentendi.mp3', True)
        saiuDeteccao = False
        comando_robo(reconhecimento, tempoMic)

def mao_reconhecida(reconheceu):
    if reconheceu == True:
        cria_audio('Sua mão foi detectada.', 'detect.mp3', True)
    else:
        cria_audio('Não estou detectando sua mão, por favor, ponha na visão da câmera.', 'saiudetect.mp3', True)


def pedra_papel_tesoura(reconheceu):
    if reconheceu == True:
        cria_audio('Você está pronto para jogar?', 'pergunta.mp3', False)
        fala('pergunta.mp3', 2)
        comando_robo(reconheceu, 4)

def checar_mao(saiu):
    while saiu == False:
        reconhecimento_de_imagem()

def jogada_player():
    global url, listaDosNomes, mpMao, maos, mpDesenho
    imgSite = urllib.request.urlopen(url)
    imgNp = np.array(bytearray(imgSite.read()), dtype=np.uint8)
    img = cv2.imdecode(imgNp, -1)
    x, y, c = img.shape

    frameBGR = cv2.flip(img, 1)
    frameRGB = cv2.cvtColor(frameBGR, cv2.COLOR_BGR2RGB)

    resultado = maos.process(frameRGB)
    nomeDoGesto = ''

    if resultado.multi_hand_landmarks:
        marcacoes = []
        for maosCoordenadas in resultado.multi_hand_landmarks:
            for coordenadas in maosCoordenadas.landmark:
                coordenadax = int(coordenadas.x * x)
                coordenaday = int(coordenadas.y * y)
                mpDesenho.draw_landmarks(frameBGR, maosCoordenadas, mpMao.HAND_CONNECTIONS)
                marcacoes.append([coordenadax,coordenaday])
            prediction = modelo.predict([marcacoes])
            maiorNumero = np.argmax(prediction)
            nomeDoGesto = listaDosNomes[maiorNumero]
            return nomeDoGesto
    if cv2.waitKey(1) == ord('q'):
        pass

def jogo(jogadaM, jogadaP):
    global condicao, comando, saiuDeteccao, umaVezSaiu, umaVezEntrou, saiuNoComando, PPT, deNovo
    if deNovo == False:
        cria_audio('Você jogou:' + jogadaP + 'Eu joguei:' + jogadaM, 'jogadaP' + jogadaP + 'jogadaM' + jogadaM + '.mp3', True)
        if (jogadaP == 'Pedra' and jogadaM == 'Tesoura') or (jogadaP == 'Tesoura' and jogadaM == 'Papel') or (jogadaP == 'Papel' and jogadaM == 'Pedra'):
            cria_audio('Você venceu, meus parabéns!', 'uwin.mp3', False)
            urllib.request.urlopen(urlRock)
            fala('uwin.mp3', 0)
            urllib.request.urlopen(urlPapel)
            pergunta = True
        elif (jogadaM == 'Pedra' and jogadaP == 'Tesoura') or (jogadaM == 'Tesoura' and jogadaP == 'Papel') or (jogadaM == 'Papel' and jogadaP == 'Pedra'):
            cria_audio('Você perdeu, eu venci!', 'iwin.mp3', False)
            urllib.request.urlopen(urlRock)
            fala('iwin.mp3', 0)
            urllib.request.urlopen(urlPapel)
            pergunta = True
        elif jogadaM == jogadaP:
            cria_audio('Nós empatamos', 'empate.mp3', True)
            urllib.request.urlopen(urlRock)
            sleep(0.5)
            urllib.request.urlopen(urlPapel)
        deNovo = True
    cria_audio('Você gostaria de jogar novamente?', 'again.mp3', False)
    fala('again.mp3', 1)
    frase = ouvir_microfone(3)
    if frase == 'sim':
        checar_mao(saiuDeteccao)
        cria_audio('Pedra... Papel... e... TESOURA!', 'ppt.mp3', True)
        sleep(1)
        jogadaPlayer = jogada_player()
        while jogadaPlayer == None:
            jogadaPlayer = jogada_player()
        print(jogadaPlayer)
        jogadaMaquina = jogadas[randint(0, 2)]
        print(jogadaMaquina)
        if jogadaMaquina == 'Pedra':
            urllib.request.urlopen(urlPedra)
        elif jogadaMaquina == 'Tesoura':
            urllib.request.urlopen(urlTesoura)
        elif jogadaMaquina == 'Papel':
            urllib.request.urlopen(urlPapel)
        deNovo = False
        jogo(jogadaMaquina, jogadaPlayer)
    elif frase == 'não':
        cria_audio('Ok, qualquer coisa é só pedir para me ativar novamente! Até logo!', 'bye.mp3', False)
        urllib.request.urlopen(urlPapel)
        urllib.request.urlopen(urlAtivar)
        condicao = False
        comando = False
        saiuDeteccao = False
        umaVezSaiu = False
        umaVezEntrou = False
        saiuNoComando = False
        PPT = True
        deNovo = False
    else:
        cria_audio('Não entendi o comando, repita.', 'naoentendi.mp3', False)
        fala('naoentendi.mp3', 0)
        jogo(jogadaM, jogadaP)

#utilizar a biblioteca para reconhecer a mão
mpMao = mp.solutions.hands
maos = mpMao.Hands(max_num_hands=1, min_detection_confidence=0.7) #reconhecimento de uma mão e min_detection_confidence são quantos % para a detecção ser considerada sucesso
mpDesenho = mp.solutions.drawing_utils #desenhar os vértices

#modelos do gestos
modelo = load_model('mp_hand_gesture')

#pegar os nomes das poses
nomeDosGestos = open('pedra papel e tesoura.names', 'r')
listaDosNomes = nomeDosGestos.read().split('\n')
nomeDosGestos.close()

url = 'http://192.168.50.111/cam-hi.jpg'
urlPisca = 'http://192.168.50.111/identificando-mao'
urlFlash = 'http://192.168.50.111/flash'
urlAtivar = 'http://192.168.50.111/ativar'
urlPedra = 'http://192.168.50.111/pedra'
urlPapel = 'http://192.168.50.111/papel'
urlTesoura = 'http://192.168.50.111/tesoura'
urlRock = 'http://192.168.50.111/rock'
urlMeio = 'http://192.168.50.111/meio'

condicao = False
comando = False
saiuDeteccao = False
umaVezSaiu = False
umaVezEntrou = False
saiuNoComando = False
PPT = False
deNovo = False
jogadas = {0:'Pedra', 1:'Papel', 2:'Tesoura'}

while True:
    while condicao == False:
        comando_chamar(urlPisca)
        PPT = False
    while comando == True:
        comando_robo(False, 4)
    reconhecimento_de_imagem()
    urllib.request.urlopen('http://192.168.50.111/flash-desligado')

urllib.request.urlopen('http://192.168.50.111/flash-desligado')
cv2.destroyAllWindows()
