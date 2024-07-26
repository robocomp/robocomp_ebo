#!/bin/bash
# Abrir Yakuake
yakuake &
# Esperar un momento para que Yakuake se abra completamente
sleep 3

# Definir las rutas
ruta1="../components/dsr-graph/components/idserver"
ruta2="../agents/asr_agent"
ruta3="../agents/llama_agent"
ruta4="../agents/tts_agent"
ruta5="../agents/therapist_app_agent"

# Función para abrir una nueva pestaña en Yakuake y ejecutar un comando en ella
function abrir_nueva_pestania() {
    xdotool key ctrl+shift+t
    sleep 0.5
    xdotool type "$1"
    xdotool key Return
}

# Abrir la primera ruta en la pestaña inicial
xdotool type "cd $ruta1"
xdotool key Return

# Abrir las siguientes tres rutas en nuevas pestañas
abrir_nueva_pestania "cd $ruta2"
abrir_nueva_pestania "cd $ruta3"
abrir_nueva_pestania "cd $ruta4"
abrir_nueva_pestania "cd $ruta5"