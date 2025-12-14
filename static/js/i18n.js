const traducciones = {
  es: {
    "recomendador_titulo": "🕝 Recomendador de municipios",
    "recomendador_subtitulo": "Indica la importancia relativa (de 0 a 5) que le das a cada dimensión. También puedes filtrar por tipo de municipio según su tamaño poblacional.",
    "economia": "💼 Economía:",
    "educacion": "📚 Educación:",
    "salud": "🏥 Sanidad:",
    "transporte": "🚌 Transporte:",
    "housing": "🏡 Vivienda:",
    "tipo_municipio": "🧬 Tipo de municipio:",
    "calcular_btn": "🔍 Calcular recomendación",
    "voz_usar": "🎤 Usar voz",
  },
  en: {
    "recomendador_titulo": "🕝 Municipality Recommender",
    "recomendador_subtitulo": "Indicate the relative importance (from 0 to 5) of each dimension. You can also filter by municipality type based on population size.",
    "economia": "💼 Economy:",
    "educacion": "📚 Education:",
    "salud": "🏥 Healthcare:",
    "transporte": "🚌 Transport:",
    "housing": "🏡 Housing:",
    "tipo_municipio": "🧬 Municipality type:",
    "calcular_btn": "🔍 Calculate recommendation",
    "voz_usar": "🎤 Use voice input",
  }
};

function traducir(lang) {
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (traducciones[lang] && traducciones[lang][key]) {
      if (el.tagName === "INPUT" || el.tagName === "SELECT") {
        el.placeholder = traducciones[lang][key];
      } else {
        el.innerText = traducciones[lang][key];
      }
    }
  });
}

function cambiarIdioma() {
  const lang = document.getElementById("idioma-selector").value;
  traducir(lang);
}

// 🎤 Entrada por voz con asignación automática
function iniciarVoz() {
  const status = document.getElementById("voz-status");
  if (!('webkitSpeechRecognition' in window)) {
    status.innerText = "🚫 Tu navegador no soporta entrada por voz.";
    return;
  }

  const recogedor = new webkitSpeechRecognition();
  recogedor.lang = 'es-ES';
  recogedor.continuous = false;
  recogedor.interimResults = false;

  recogedor.onstart = () => { status.innerText = "⏳ Escuchando..."; };
  recogedor.onerror = () => { status.innerText = "❌ Error de reconocimiento."; };
  recogedor.onend = () => { status.innerText = "✅ Finalizado."; };

  recogedor.onresult = function (event) {
    const frase = event.results[0][0].transcript.toLowerCase();
    const mapeo = {
      economia: "economia",
      educación: "educacion",
      sanidad: "salud",
      salud: "salud",
      transporte: "transporte",
      vivienda: "housing"
    };

    for (let palabra in mapeo) {
      if (frase.includes(palabra)) {
        const valor = frase.match(/\d+/);
        if (valor) {
          const id = mapeo[palabra];
          document.getElementById(id).value = parseInt(valor[0]);
          status.innerText = `✅ Asignado: ${palabra} = ${valor[0]}`;
        }
      }
    }
  };

  recogedor.start();
}
