#Librerías necesarias para el funcionamiento del juego
import streamlit as st
import os
import time as tm
import random
import base64
import json
from PIL import Image
from streamlit_autorefresh import st_autorefresh

#Configuración inicial para aspecto visual de la página
st.set_page_config(page_title = "PixMatch", page_icon="🕹️", layout = "wide", initial_sidebar_state = "expanded")
#Obtención del Directorio actual
vDrive = os.path.splitdrive(os.getcwd())[0]
#Instrucción para ubicarnos en el entorno de trabajo del Proyecto
vpth = "./"

#Fragmento de código HTML para el estilo de la página
sbe = """<span style='font-size: 140px;
                      border-radius: 7px;
                      text-align: center;
                      display:inline;
                      padding-top: 3px;
                      padding-bottom: 3px;
                      padding-left: 0.4em;
                      padding-right: 0.4em;
                      '>
                      |fill_variable|
                      </span>"""
#Definición del estilo de los emojis
pressed_emoji = """<span style='font-size: 24px;
                                border-radius: 7px;
                                text-align: center;
                                display:inline;
                                padding-top: 3px;
                                padding-bottom: 3px;
                                padding-left: 0.2em;
                                padding-right: 0.2em;
                                '>
                                |fill_variable|
                                </span>"""
#Estilo del Menú Principal
horizontal_bar = "<hr style='margin-top: 0; margin-bottom: 0; height: 1px; border: 1px solid #635985;'><br>"

purple_btn_colour = """
                        <style>
                            div.stButton > button:first-child {background-color: #4b0082; color:#ffffff;}
                            div.stButton > button:hover {background-color: RGB(0,112,192); color:#ffffff;}
                            div.stButton > button:focus {background-color: RGB(47,117,181); color:#ffffff;}
                        </style>
                    """

mystate = st.session_state  # Accede al estado de sesión de la aplicación

# Inicialización de variables en el estado de sesión si no existen previamente:
if "expired_cells" not in mystate: mystate.expired_cells = []  # Lista de celdas expiradas
if "myscore" not in mystate: mystate.myscore = 0  # Puntuación del jugador
if "plyrbtns" not in mystate: mystate.plyrbtns = {}  # Botones del jugador
if "sidebar_emoji" not in mystate: mystate.sidebar_emoji = ''  # Emoji en la barra lateral
if "emoji_bank" not in mystate: mystate.emoji_bank = []  # Banco de emojis disponibles
if "GameDetails" not in mystate:
    mystate.GameDetails = ['Medium', 6, 7, '']  # Detalles del juego: dificultad, intervalo de autogeneración, celdas por fila/columna, nombre del jugador

def ReduceGapFromPageTop(wch_section='main page'):
    """
    ReduceGapFromPageTop ajusta el espacio entre la parte superior de la página y las secciones específicas.
    Parámetros:
    - wch_section (str): La sección para la cual se desea ajustar el espacio. Puede ser 'main page' para la página principal,
                         'sidebar' para la barra lateral o 'all' para ambas.
    """
    if wch_section == 'main page':
        # Si la sección especificada es la página principal, ajusta el relleno superior de los contenedores de bloques en la página principal.
        st.markdown("<style> div[class^='block-container'] { padding-top: 2rem; } </style>", True)
    elif wch_section == 'sidebar':
        # Si la sección especificada es la barra lateral, ajusta el relleno superior de los elementos en la barra lateral.
        st.markdown("<style> div[class^='st-emotion-cache-10oheav'] { padding-top: 0rem; } </style>", True)
    elif wch_section == 'all':
        # Si se especifica 'all', ajusta tanto la página principal como la barra lateral.
        st.markdown("<style> div[class^='block-container'] { padding-top: 2rem; } </style>", True)  # Página principal
        st.markdown("<style> div[class^='st-emotion-cache-10oheav'] { padding-top: 0rem; } </style>", True)  # Barra lateral


def Leaderboard(what_to_do):
    """
    Leaderboard administra el tablero de líderes del juego.

    Parámetros:
    - what_to_do (str): La acción a realizar ('create' para crear, 'write' para escribir, 'read' para leer).

    """

    if what_to_do == 'create':
        # Si se solicita crear el tablero de líderes y el nombre del jugador está presente, crea un nuevo archivo JSON si no existe.
        if mystate.GameDetails[3] != '' and not os.path.isfile(vpth + 'leaderboard.json'):
            tmpdict = {}
            json.dump(tmpdict, open(vpth + 'leaderboard.json', 'w'))  # Escribir archivo

    elif what_to_do == 'write':
        # Si se solicita escribir en el tablero de líderes y el nombre del jugador está presente, registra la puntuación en el tablero.
        if mystate.GameDetails[3] != '':
            if os.path.isfile(vpth + 'leaderboard.json'):
                leaderboard = json.load(open(vpth + 'leaderboard.json'))  # Leer archivo
                leaderboard_dict_lngth = len(leaderboard)

                # Agregar el nuevo puntaje al tablero y ordenarlo de forma descendente.
                leaderboard[str(leaderboard_dict_lngth + 1)] = {'NameCountry': mystate.GameDetails[3],
                                                                'HighestScore': mystate.myscore}
                leaderboard = dict(sorted(leaderboard.items(), key=lambda item: item[1]['HighestScore'], reverse=True))

                # Mantener solo los primeros 4 puntajes.
                if len(leaderboard) > 4:
                    for i in range(len(leaderboard) - 4):
                        leaderboard.popitem()  # Eliminar la última entrada

                json.dump(leaderboard, open(vpth + 'leaderboard.json', 'w'))  # Escribir archivo

    elif what_to_do == 'read':
        # Si se solicita leer el tablero de líderes y el nombre del jugador está presente, muestra los mejores puntajes.
        if mystate.GameDetails[3] != '':
            if os.path.isfile(vpth + 'leaderboard.json'):
                leaderboard = json.load(open(vpth + 'leaderboard.json'))  # Leer archivo

                # Ordenar el tablero de líderes de forma descendente.
                leaderboard = dict(sorted(leaderboard.items(), key=lambda item: item[1]['HighestScore'], reverse=True))

                # Mostrar los mejores 4 puntajes en columnas separadas.
                sc0, sc1, sc2, sc3 = st.columns((3, 4, 4, 4))
                rknt = 0
                for vkey in leaderboard.keys():
                    if leaderboard[vkey]['NameCountry'] != '':
                        rknt += 1
                        if rknt == 1:
                            sc0.write('🏆 Past Winners:')
                            sc1.write(
                                f"🥇 | {leaderboard[vkey]['NameCountry']}: :red[{leaderboard[vkey]['HighestScore']}]")
                        elif rknt == 2:
                            sc2.write(
                                f"🥈 | {leaderboard[vkey]['NameCountry']}: :red[{leaderboard[vkey]['HighestScore']}]")
                        elif rknt == 3:
                            sc3.write(
                                f"🥉 | {leaderboard[vkey]['NameCountry']}: :red[{leaderboard[vkey]['HighestScore']}]")
                        elif rknt == 4:
                            sc3.write(
                                f"4️ | {leaderboard[vkey]['NameCountry']}: :red[{leaderboard[vkey]['HighestScore']}]")



def InitialPage():
    """
    InitialPage muestra la página inicial del juego.

    """

    # Sección de la barra lateral
    with st.sidebar:
        # Encabezado de la barra lateral
        st.subheader("🖼️ Pix Match:")
        # Línea horizontal decorativa
        st.markdown(horizontal_bar, True)

        # Cargar y mostrar el logo en la barra lateral
        sidebarlogo = Image.open('sidebarlogo.jpg').resize((300, 390))
        st.image(sidebarlogo, use_column_width='auto')

    # Sección principal de la página
    # Mostrar las instrucciones y reglas del juego
    hlp_dtl = """
    <span style="font-size: 26px;">
    <ol>
    <li style="font-size:15px";>Game play opens with (a) a sidebar picture and (b) a N x N grid of picture buttons, where N=6:Easy, N=7:Medium, N=8:Hard.</li>
    <li style="font-size:15px";>You need to match the sidebar picture with a grid picture button, by pressing the (matching) button (as quickly as possible).</li>
    <li style="font-size:15px";>Each correct picture match will earn you <strong>+N</strong> points (where N=5:Easy, N=3:Medium, N=1:Hard); each incorrect picture match will earn you <strong>-1</strong> point.</li>
    <li style="font-size:15px";>The sidebar picture and the grid pictures will dynamically regenerate after a fixed seconds interval (Easy=8, Medium=6, Hard=5). Each regeneration will have a penalty of <strong>-1</strong> point</li>
    <li style="font-size:15px";>Each of the grid buttons can only be pressed once during the entire game.</li>
    <li style="font-size:15px";>The game completes when all the grid buttons are pressed.</li>
    <li style="font-size:15px";>At the end of the game, if you have a positive score, you will have <strong>won</strong>; otherwise, you will have <strong>lost</strong>.</li>
    </ol></span>"""

    # Sección para mostrar las instrucciones y reglas del juego
    sc1, sc2 = st.columns(2)
    # Cargar y mostrar una imagen de ayuda aleatoria
    random.seed()
    GameHelpImg = vpth + random.choice(["MainImg1.jpg", "MainImg2.jpg", "MainImg3.jpg", "MainImg4.jpg"])
    GameHelpImg = Image.open(GameHelpImg).resize((550, 550))
    sc2.image(GameHelpImg, use_column_width='auto')

    # Mostrar las instrucciones y reglas del juego en formato de lista ordenada
    sc1.subheader('Rules | Playing Instructions:')
    sc1.markdown(horizontal_bar, True)
    sc1.markdown(hlp_dtl, unsafe_allow_html=True)
    st.markdown(horizontal_bar, True)

    # Información del autor
    author_dtl = "<strong>Happy Playing: 😎 Shawn Pereira: shawnpereira1969@gmail.com</strong>"
    st.markdown(author_dtl, unsafe_allow_html=True)


def ReadPictureFile(wch_fl):
    """
    ReadPictureFile lee un archivo de imagen y devuelve su representación base64.

    Parámetros:
    - wch_fl (str): Nombre del archivo de imagen.

    Returns:
    - str: Representación base64 del archivo de imagen.
    """

    try:
        pxfl = f"{vpth}{wch_fl}"  # Ruta completa del archivo de imagen
        # Leer el archivo de imagen en modo binario, codificarlo en base64 y decodificarlo como una cadena
        return base64.b64encode(open(pxfl, 'rb').read()).decode()

    except:
        return ""  # En caso de error, devuelve una cadena vacía


def PressedCheck(vcell):
    """
    PressedCheck verifica si una celda de botón ha sido presionada y realiza las acciones correspondientes.

    Parámetros:
    - vcell (str): Identificador de la celda de botón.

    """

    if mystate.plyrbtns[vcell]['isPressed'] == False:
        mystate.plyrbtns[vcell]['isPressed'] = True  # Marcar la celda como presionada
        mystate.expired_cells.append(vcell)  # Agregar la celda a la lista de celdas expiradas

        # Verificar si el emoji de la celda coincide con el emoji de la barra lateral
        if mystate.plyrbtns[vcell]['eMoji'] == mystate.sidebar_emoji:
            mystate.plyrbtns[vcell]['isTrueFalse'] = True  # Marcar como verdadero
            mystate.myscore += 5  # Incrementar la puntuación

            # Incrementar la puntuación adicional según la dificultad del juego
            if mystate.GameDetails[0] == 'Easy':
                mystate.myscore += 5
            elif mystate.GameDetails[0] == 'Medium':
                mystate.myscore += 3
            elif mystate.GameDetails[0] == 'Hard':
                mystate.myscore += 1

        else:
            mystate.plyrbtns[vcell]['isTrueFalse'] = False  # Marcar como falso
            mystate.myscore -= 1  # Decrementar la puntuación en caso de error


def ResetBoard():
    """
    ResetBoard reinicia el tablero del juego con un nuevo emoji de la barra lateral y emojis aleatorios en los botones.

    """

    total_cells_per_row_or_col = mystate.GameDetails[2]  # Obtener el número total de celdas por fila o columna

    # Seleccionar aleatoriamente un emoji de la barra lateral y asignarlo a la variable de estado
    sidebar_emoji_no = random.randint(1, len(mystate.emoji_bank)) - 1
    mystate.sidebar_emoji = mystate.emoji_bank[sidebar_emoji_no]

    sidebar_emoji_in_list = False

    # Asignar emojis aleatorios a las celdas de los botones
    for vcell in range(1, ((total_cells_per_row_or_col ** 2) + 1)):
        rndm_no = random.randint(1, len(mystate.emoji_bank)) - 1
        if mystate.plyrbtns[vcell]['isPressed'] == False:
            vemoji = mystate.emoji_bank[rndm_no]
            mystate.plyrbtns[vcell]['eMoji'] = vemoji
            if vemoji == mystate.sidebar_emoji:
                sidebar_emoji_in_list = True

    # Si el emoji de la barra lateral no está en la lista de emojis de los botones, agregarlo aleatoriamente
    if sidebar_emoji_in_list == False:
        tlst = [x for x in range(1, ((total_cells_per_row_or_col ** 2) + 1))]
        flst = [x for x in tlst if x not in mystate.expired_cells]
        if len(flst) > 0:
            lptr = random.randint(0, (len(flst) - 1))
            lptr = flst[lptr]
            mystate.plyrbtns[lptr]['eMoji'] = mystate.sidebar_emoji


def PreNewGame():
    """
    PreNewGame prepara el juego para una nueva partida reiniciando las variables de estado y seleccionando emojis para el juego.

    """

    total_cells_per_row_or_col = mystate.GameDetails[2]  # Obtener el número total de celdas por fila o columna
    mystate.expired_cells = []  # Reiniciar la lista de celdas expiradas
    mystate.myscore = 0  # Reiniciar la puntuación del jugador

    # Listas de emojis disponibles para el juego
    foxes = ['😺', '😸', '😹', '😻', '😼', '😽', '🙀', '😿', '😾']
    emojis = ['😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇', '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜', '🤪', '🤨', '🧐', '🤓', '😎', '🤩', '🥳', '😏', '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣', '😖', '😫', '😩', '🥺', '😢', '😠', '😳', '😥', '😓', '🤗', '🤔', '🤭', '🤫', '🤥', '😶', '😐', '😑', '😬', '🙄', '😯', '😧', '😮', '😲', '🥱', '😴', '🤤', '😪', '😵', '🤐', '🥴', '🤒']
    humans = ['👶', '👧', '🧒', '👦', '👩', '🧑', '👨', '👩‍🦱', '👨‍🦱', '👩‍🦰', '‍👨', '👱', '👩', '👱', '👩‍', '👨‍🦳', '👩‍🦲', '👵', '🧓', '👴', '👲', '👳']
    foods = ['🍏', '🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🍈', '🍒', '🍑', '🥭', '🍍', '🥥', '🥝', '🍅', '🍆', '🥑', '🥦', '🥬', '🥒', '🌽', '🥕', '🧄', '🧅', '🥔', '🍠', '🥐', '🥯', '🍞', '🥖', '🥨', '🧀', '🥚', '🍳', '🧈', '🥞', '🧇', '🥓', '🥩', '🍗', '🍖', '🦴', '🌭', '🍔', '🍟', '🍕']
    clocks = ['🕓', '🕒', '🕑', '🕘', '🕛', '🕚', '🕖', '🕙', '🕔', '🕤', '🕠', '🕕', '🕣', '🕞', '🕟', '🕜', '🕢', '🕦']
    hands = ['🤚', '🖐', '✋', '🖖', '👌', '🤏', '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉', '👆', '🖕', '👇', '☝️', '👍', '👎', '✊', '👊', '🤛', '🤜', '👏', '🙌', '🤲', '🤝', '🤚🏻', '🖐🏻', '✋🏻', '🖖🏻', '👌🏻', '🤏🏻', '✌🏻', '🤞🏻', '🤟🏻', '🤘🏻', '🤙🏻', '👈🏻', '👉🏻', '👆🏻', '🖕🏻', '👇🏻', '☝🏻', '👍🏻', '👎🏻', '✊🏻', '👊🏻', '🤛🏻', '🤜🏻', '👏🏻', '🙌🏻', '🤚🏽', '🖐🏽', '✋🏽', '🖖🏽', '👌🏽', '🤏🏽', '✌🏽', '🤞🏽', '🤟🏽', '🤘🏽', '🤙🏽', '👈🏽', '👉🏽', '👆🏽', '🖕🏽', '👇🏽', '☝🏽', '👍🏽', '👎🏽', '✊🏽', '👊🏽', '🤛🏽', '🤜🏽', '👏🏽', '🙌🏽']
    animals = ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐮', '🐷', '🐽', '🐸', '🐵', '🙈', '🙉', '🙊', '🐒', '🐔', '🐧', '🐦', '🐤', '🐣', '🐥', '🦆', '🦅', '🦉', '🦇', '🐺', '🐗', '🐴', '🦄', '🐝', '🐛', '🦋', '🐌', '🐞', '🐜', '🦟', '🦗', '🦂', '🐢', '🐍', '🦎', '🦖', '🦕', '🐙', '🦑', '🦐', '🦞', '🦀', '🐡', '🐠', '🐟', '🐬', '🐳', '🐋', '🦈', '🐊', '🐅', '🐆', '🦓', '🦍', '🦧', '🐘', '🦛', '🦏', '🐪', '🐫', '🦒', '🦘', '🐃', '🐂', '🐄', '🐎', '🐖', '🐏', '🐑', '🦙', '🐐', '🦌', '🐕', '🐩', '🦮', '🐕‍🦺', '🐈', '🐓', '🦃', '🦚', '🦜', '🦢', '🦩', '🐇', '🦝', '🦨', '🦦', '🦥', '🐁', '🐀', '🦔']
    vehicles = ['🚗', '🚕', '🚙', '🚌', '🚎', '🚓', '🚑', '🚒', '🚐', '🚚', '🚛', '🚜', '🦯', '🦽', '🦼', '🛴', '🚲', '🛵', '🛺', '🚔', '🚍', '🚘', '🚖', '🚡', '🚠', '🚟', '🚃', '🚋', '🚞', '🚝', '🚄', '🚅', '🚈', '🚂', '🚆', '🚇', '🚊', '🚉', '✈️', '🛫', '🛬', '💺', '🚀', '🛸', '🚁', '🛶', '⛵️', '🚤', '🛳', '⛴', '🚢']
    houses = ['🏠', '🏡', '🏘', '🏚', '🏗', '🏭', '🏢', '🏬', '🏣', '🏤', '🏥', '🏦', '🏨', '🏪', '🏫', '🏩', '💒', '🏛', '⛪️', '🕌', '🕍', '🛕']
    purple_signs = ['☮️', '✝️', '☪️', '☸️', '✡️', '🔯', '🕎', '☯️', '☦️', '🛐', '⛎', '♈️', '♉️', '♊️', '♋️', '♌️', '♍️', '♎️', '♏️', '♐️', '♑️', '♒️', '♓️', '🆔', '🈳']
    red_signs = ['🈶', '🈚️', '🈸', '🈺', '🈷️', '✴️', '🉐', '㊙️', '㊗️', '🈴', '🈵', '🈹', '🈲', '🅰️', '🅱️', '🆎', '🆑', '🅾️', '🆘', '🚼', '🛑', '⛔️', '📛', '🚫', '🚷', '🚯', '🚳', '🚱', '🔞', '📵', '🚭']
    blue_signs = ['🚾', '♿️', '🅿️', '🈂️', '🛂', '🛃', '🛄', '🛅', '🚹', '🚺', '🚻', '🚮', '🎦', '📶', '🈁', '🔣', '🔤', '🔡', '🔠', '🆖', '🆗', '🆙', '🆒', '🆕', '🆓', '0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '🔢', '⏏️', '▶️', '⏸', '⏯', '⏹', '⏺', '⏭', '⏮', '⏩', '⏪', '⏫', '⏬', '◀️', '🔼', '🔽', '➡️', '⬅️', '⬆️', '⬇️', '↗️', '↘️', '↙️', '↖️', '↪️', '↩️', '⤴️', '⤵️', '🔀', '🔁', '🔂', '🔄', '🔃', '➿', '🔚', '🔙', '🔛', '🔝', '🔜']
    moon = ['🌕', '🌔', '🌓', '🌗', '🌒', '🌖', '🌑', '🌜', '🌛', '🌙']

    random.seed()

    # Selección aleatoria de emojis según la dificultad del juego
    if mystate.GameDetails[0] == 'Easy':
        wch_bank = random.choice(['foods', 'moon', 'animals'])
        mystate.emoji_bank = locals()[wch_bank]

    elif mystate.GameDetails[0] == 'Medium':
        wch_bank = random.choice(['foxes', 'emojis', 'humans', 'vehicles', 'houses', 'hands', 'purple_signs', 'red_signs', 'blue_signs'])
        mystate.emoji_bank = locals()[wch_bank]

    elif mystate.GameDetails[0] == 'Hard':
        wch_bank = random.choice(['foxes', 'emojis', 'humans', 'foods', 'clocks', 'hands', 'animals', 'vehicles', 'houses', 'purple_signs', 'red_signs', 'blue_signs', 'moon'])
        mystate.emoji_bank = locals()[wch_bank]

    # Inicializar el diccionario de botones del jugador
    mystate.plyrbtns = {}
    for vcell in range(1, ((total_cells_per_row_or_col ** 2) + 1)):
        mystate.plyrbtns[vcell] = {'isPressed': False, 'isTrueFalse': False, 'eMoji': ''}


def ScoreEmoji():
    # Asigna un emoji según el puntaje del jugador
    if mystate.myscore == 0:
        return '😐'
    elif -5 <= mystate.myscore <= -1:
        return '😏'
    elif -10 <= mystate.myscore <= -6:
        return '☹️'
    elif mystate.myscore <= -11:
        return '😖'
    elif 1 <= mystate.myscore <= 5:
        return '🙂'
    elif 6 <= mystate.myscore <= 10:
        return '😊'
    elif mystate.myscore > 10:
        return '😁'


def NewGame():
    # Reinicia el tablero y muestra la interfaz para un nuevo juego
    ResetBoard()  # Reiniciar el tablero
    total_cells_per_row_or_col = mystate.GameDetails[2]  # Obtener el tamaño del tablero

    ReduceGapFromPageTop('sidebar')  # Ajustar el espacio en la barra lateral
    with st.sidebar:
        # Configuración de la barra lateral
        st.subheader(f"🖼️ Pix Match: {mystate.GameDetails[0]}")
        st.markdown(horizontal_bar, True)

        # Mostrar la puntuación y los detalles del juego
        st.markdown(sbe.replace('|fill_variable|', mystate.sidebar_emoji), True)
        aftimer = st_autorefresh(interval=(mystate.GameDetails[1] * 1000), key="aftmr")
        if aftimer > 0: mystate.myscore -= 1
        st.info(
            f"{ScoreEmoji()} Score: {mystate.myscore} | Pending: {(total_cells_per_row_or_col ** 2) - len(mystate.expired_cells)}")
        st.markdown(horizontal_bar, True)

        # Botón para volver a la página principal
        if st.button(f"🔙 Return to Main Page", use_container_width=True):
            mystate.runpage = Main
            st.rerun()

    Leaderboard('read')  # Mostrar la tabla de clasificación
    st.subheader("Picture Positions:")
    st.markdown(horizontal_bar, True)

    # Configuración del tablero
    st.markdown("<style> div[class^='css-1vbkxwb'] > p { font-size: 1.5rem; } </style> ",
                unsafe_allow_html=True)  # Ajustar el tamaño de los botones

    # Dividir el tablero en columnas
    for i in range(1, (total_cells_per_row_or_col + 1)):
        tlst = ([1] * total_cells_per_row_or_col) + [2]  # 2 = espacio adicional a la derecha
        globals()['cols' + str(i)] = st.columns(tlst)

    # Iterar sobre cada celda del tablero
    for vcell in range(1, (total_cells_per_row_or_col ** 2) + 1):
        if 1 <= vcell <= (total_cells_per_row_or_col * 1):
            arr_ref = '1'
            mval = 0
        elif ((total_cells_per_row_or_col * 1) + 1) <= vcell <= (total_cells_per_row_or_col * 2):
            arr_ref = '2'
            mval = (total_cells_per_row_or_col * 1)

        elif ((total_cells_per_row_or_col * 2)+1) <= vcell <= (total_cells_per_row_or_col * 3):
            arr_ref = '3'
            mval = (total_cells_per_row_or_col * 2)

        elif ((total_cells_per_row_or_col * 3)+1) <= vcell <= (total_cells_per_row_or_col * 4):
            arr_ref = '4'
            mval = (total_cells_per_row_or_col * 3)

        elif ((total_cells_per_row_or_col * 4)+1) <= vcell <= (total_cells_per_row_or_col * 5):
            arr_ref = '5'
            mval = (total_cells_per_row_or_col * 4)

        elif ((total_cells_per_row_or_col * 5)+1) <= vcell <= (total_cells_per_row_or_col * 6):
            arr_ref = '6'
            mval = (total_cells_per_row_or_col * 5)

        elif ((total_cells_per_row_or_col * 6)+1) <= vcell <= (total_cells_per_row_or_col * 7):
            arr_ref = '7'
            mval = (total_cells_per_row_or_col * 6)

        elif ((total_cells_per_row_or_col * 7)+1) <= vcell <= (total_cells_per_row_or_col * 8):
            arr_ref = '8'
            mval = (total_cells_per_row_or_col * 7)

        elif ((total_cells_per_row_or_col * 8)+1) <= vcell <= (total_cells_per_row_or_col * 9):
            arr_ref = '9'
            mval = (total_cells_per_row_or_col * 8)

        elif ((total_cells_per_row_or_col * 9)+1) <= vcell <= (total_cells_per_row_or_col * 10):
            arr_ref = '10'
            mval = (total_cells_per_row_or_col * 9)

        # Limpiar la celda y mostrar el emoji si está presionado
        globals()['cols' + arr_ref][vcell - mval] = globals()['cols' + arr_ref][vcell - mval].empty()
        if mystate.plyrbtns[vcell]['isPressed'] == True:
            if mystate.plyrbtns[vcell]['isTrueFalse'] == True:
                globals()['cols' + arr_ref][vcell - mval].markdown(pressed_emoji.replace('|fill_variable|', '✅️'), True)
            elif mystate.plyrbtns[vcell]['isTrueFalse'] == False:
                globals()['cols' + arr_ref][vcell - mval].markdown(pressed_emoji.replace('|fill_variable|', '❌'), True)
        else:
            vemoji = mystate.plyrbtns[vcell]['eMoji']
            globals()['cols' + arr_ref][vcell - mval].button(vemoji, on_click=PressedCheck, args=(vcell,),
                                                             key=f"B{vcell}")

    st.caption('')  # Relleno vertical
    st.markdown(horizontal_bar, True)

    # Comprobar si se completaron todas las celdas
    if len(mystate.expired_cells) == (total_cells_per_row_or_col ** 2):
        Leaderboard('write')  # Actualizar la tabla de clasificación

        # Mostrar efectos especiales según el puntaje
        if mystate.myscore > 0:
            st.balloons()
        elif mystate.myscore <= 0:
            st.snow()

        # Esperar y volver a la página principal
        tm.sleep(5)
        mystate.runpage = Main
        st.rerun()


def Main():
    # Estilo para reducir el ancho de la barra lateral y color de fondo de los botones
    st.markdown('<style>[data-testid="stSidebar"] > div:first-child {width: 310px;}</style>', unsafe_allow_html=True)
    st.markdown(purple_btn_colour, unsafe_allow_html=True)

    # Mostrar la página inicial
    InitialPage()

    # Barra lateral para configurar el juego y comenzar una nueva partida
    with st.sidebar:
        # Configuración del nivel de dificultad y nombre del jugador
        mystate.GameDetails[0] = st.radio('Difficulty Level:', options=('Easy', 'Medium', 'Hard'), index=1, horizontal=True)
        mystate.GameDetails[3] = st.text_input("Player Name, Country", placeholder='Shawn Pereira, India', help='Optional input only for Leaderboard')

        # Botón para iniciar una nueva partida
        if st.button(f"🕹️ New Game", use_container_width=True):
            # Configuración de detalles del juego según el nivel de dificultad seleccionado
            if mystate.GameDetails[0] == 'Easy':
                mystate.GameDetails[1] = 8  # Intervalo de tiempo en segundos
                mystate.GameDetails[2] = 6  # Número total de celdas por fila o columna
            elif mystate.GameDetails[0] == 'Medium':
                mystate.GameDetails[1] = 6
                mystate.GameDetails[2] = 7
            elif mystate.GameDetails[0] == 'Hard':
                mystate.GameDetails[1] = 5
                mystate.GameDetails[2] = 8

            Leaderboard('create')  # Crear una nueva tabla de clasificación

            PreNewGame()  # Preparar el nuevo juego
            mystate.runpage = NewGame  # Cambiar la página en ejecución a la función NewGame
            st.rerun()  # Reiniciar la aplicación para comenzar el nuevo juego

        st.markdown(horizontal_bar, True)  # Línea horizontal separadora


# Si 'runpage' no está en mystate, se establece Main como la página inicial
if 'runpage' not in mystate:
    mystate.runpage = Main

# Ejecutar la página actualmente en ejecución
mystate.runpage()
