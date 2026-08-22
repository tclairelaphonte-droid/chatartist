// =========================================================
// langues.js — Détection automatique + traductions
// Langues : FR / EN / IT / DE / ES / FI
// =========================================================

const translations = {
  fr: {
    "nav.artistes": "Artistes",
    "nav.messages": "Messages",
    "nav.login": "Se connecter",
    "nav.register": "Rejoindre",
    "nav.logout": "Se déconnecter",
    "nav.dashboard": "Dashboard",
    "hero.eyebrow": "Plateforme officielle",
    "hero.title": "Vivez la coulisse, pas juste le concert.",
    "hero.subtitle": "Un espace unique où vos avis façonnent vraiment les prochaines chansons, les clips et les tournées. Votre voix arrive directement chez l'artiste.",
    "hero.cta": "voir son artiste",
    "artists.eyebrow": "Nos artistes",
    "artists.title": "Plusieurs univers, une seule communauté",
    "artists.subtitle": "Choisissez un artiste pour découvrir son univers et échanger directement avec l’artiste.",
    "artists.loading": "Chargement des artistes…",
    "artists.empty": "Aucun artiste publié pour le moment.",
    "artists.discover": "Découvrir →",
    "artists.conversations": "Conversations",
    "feat.1.title": "Un message, un artiste",
    "feat.1.text": "Chaque discussion démarrée depuis une page artiste lui est automatiquement associée — vous n’avez rien à sélectionner.",
    "feat.2.title": "Lu par l'artiste",
    "feat.2.text": "Vos idées de clips, vos titres préférés et vos retours arrivent directement dans le tableau de bord de l'artiste.",
    "feat.3.title": "Des décisions, pas des suppositions",
    "feat.3.text": "Les choix artistiques s’appuient sur vos retours réels : chansons, clips, événements et stratégie.",
    "cta.title": "Prêt à faire entendre votre voix ?",
    "cta.subtitle": "Créez votre compte en moins d’une minute et commencez la conversation.",
    "cta.button": "voir son artiste",
    "messages.title": "Vos conversations",
    "messages.empty": "Aucune conversation.<br>Écrivez à un artiste pour commencer.",
    "messages.error": "Impossible de charger les messages.",
    "messages.photo": "📷 Photo",
    "messages.conversation": "Conversation",
    "footer.meta": "plateforme communautaire officielle",
    "hello": "Bonjour,",
    "upload.photo": "Importer une photo"
  },

  en: {
    "nav.artistes": "Artists",
    "nav.messages": "Messages",
    "nav.login": "Log in",
    "nav.register": "Join",
    "nav.logout": "Log out",
    "nav.dashboard": "Dashboard",
    "hero.eyebrow": "Official platform",
    "hero.title": "Experience the backstage, not just the concert.",
    "hero.subtitle": "A unique space where your feedback truly shapes the next songs, music videos and tours. Your voice goes straight to the artist.",
    "hero.cta": "see the artist",
    "artists.eyebrow": "Our artists",
    "artists.title": "Multiple worlds, one community",
    "artists.subtitle": "Choose an artist to discover their universe and chat directly with them.",
    "artists.loading": "Loading artists…",
    "artists.empty": "No artists published yet.",
    "artists.discover": "Discover →",
    "artists.conversations": "Conversations",
    "feat.1.title": "One message, one artist",
    "feat.1.text": "Every conversation started from an artist page is automatically linked to them — nothing to select.",
    "feat.2.title": "Read by the artist",
    "feat.2.text": "Your ideas for videos, your favorite tracks and your feedback go straight to the artist’s dashboard.",
    "feat.3.title": "Decisions, not guesses",
    "feat.3.text": "Artistic choices are based on your real feedback: songs, videos, events and strategy.",
    "cta.title": "Ready to make your voice heard?",
    "cta.subtitle": "Create your account in under a minute and start the conversation.",
    "cta.button": "see the artist",
    "messages.title": "Your conversations",
    "messages.empty": "No conversations yet.<br>Write to an artist to get started.",
    "messages.error": "Unable to load messages.",
    "messages.photo": "📷 Photo",
    "messages.conversation": "Conversation",
    "footer.meta": "official community platform",
    "hello": "Hello,",
    "upload.photo": "Upload a photo"
  },

  it: {
    "nav.artistes": "Artisti",
    "nav.messages": "Messaggi",
    "nav.login": "Accedi",
    "nav.register": "Unisciti",
    "nav.logout": "Esci",
    "nav.dashboard": "Dashboard",
    "hero.eyebrow": "Piattaforma ufficiale",
    "hero.title": "Vivi il backstage, non solo il concerto.",
    "hero.subtitle": "Uno spazio unico dove i tuoi feedback modellano davvero le prossime canzoni, i video e i tour. La tua voce arriva direttamente all’artista.",
    "hero.cta": "vedi l’artista",
    "artists.eyebrow": "I nostri artisti",
    "artists.title": "Più universi, una sola community",
    "artists.subtitle": "Scegli un artista per scoprire il suo universo e parlare direttamente con lui.",
    "artists.loading": "Caricamento artisti…",
    "artists.empty": "Nessun artista pubblicato al momento.",
    "artists.discover": "Scopri →",
    "artists.conversations": "Conversazioni",
    "feat.1.title": "Un messaggio, un artista",
    "feat.1.text": "Ogni conversazione iniziata dalla pagina di un artista gli è automaticamente collegata — non devi selezionare nulla.",
    "feat.2.title": "Letto dall’artista",
    "feat.2.text": "Le tue idee per i video, i tuoi brani preferiti e i tuoi feedback arrivano direttamente nella dashboard dell’artista.",
    "feat.3.title": "Decisioni, non supposizioni",
    "feat.3.text": "Le scelte artistiche si basano sui tuoi feedback reali: canzoni, video, eventi e strategia.",
    "cta.title": "Pronto a far sentire la tua voce?",
    "cta.subtitle": "Crea il tuo account in meno di un minuto e inizia la conversazione.",
    "cta.button": "vedi l’artista",
    "messages.title": "Le tue conversazioni",
    "messages.empty": "Nessuna conversazione.<br>Scrivi a un artista per iniziare.",
    "messages.error": "Impossibile caricare i messaggi.",
    "messages.photo": "📷 Foto",
    "messages.conversation": "Conversazione",
    "footer.meta": "piattaforma community ufficiale",
    "hello": "Ciao,",
    "upload.photo": "Carica una foto"
  },

  de: {
    "nav.artistes": "Künstler",
    "nav.messages": "Nachrichten",
    "nav.login": "Anmelden",
    "nav.register": "Beitreten",
    "nav.logout": "Abmelden",
    "nav.dashboard": "Dashboard",
    "hero.eyebrow": "Offizielle Plattform",
    "hero.title": "Erlebe das Backstage, nicht nur das Konzert.",
    "hero.subtitle": "Ein einzigartiger Raum, in dem dein Feedback wirklich die nächsten Songs, Musikvideos und Touren formt. Deine Stimme kommt direkt beim Künstler an.",
    "hero.cta": "Künstler ansehen",
    "artists.eyebrow": "Unsere Künstler",
    "artists.title": "Mehrere Welten, eine Community",
    "artists.subtitle": "Wähle einen Künstler, um sein Universum zu entdecken und direkt mit ihm zu chatten.",
    "artists.loading": "Künstler werden geladen…",
    "artists.empty": "Noch keine Künstler veröffentlicht.",
    "artists.discover": "Entdecken →",
    "artists.conversations": "Gespräche",
    "feat.1.title": "Eine Nachricht, ein Künstler",
    "feat.1.text": "Jedes Gespräch, das von einer Künstlerseite gestartet wird, ist automatisch mit ihm verknüpft — nichts auswählen.",
    "feat.2.title": "Vom Künstler gelesen",
    "feat.2.text": "Deine Ideen für Videos, deine Lieblingssongs und dein Feedback landen direkt im Dashboard des Künstlers.",
    "feat.3.title": "Entscheidungen, keine Vermutungen",
    "feat.3.text": "Künstlerische Entscheidungen basieren auf deinem echten Feedback: Songs, Videos, Events und Strategie.",
    "cta.title": "Bereit, deine Stimme zu erheben?",
    "cta.subtitle": "Erstelle dein Konto in unter einer Minute und starte das Gespräch.",
    "cta.button": "Künstler ansehen",
    "messages.title": "Deine Gespräche",
    "messages.empty": "Noch keine Gespräche.<br>Schreibe einem Künstler, um zu starten.",
    "messages.error": "Nachrichten konnten nicht geladen werden.",
    "messages.photo": "📷 Foto",
    "messages.conversation": "Gespräch",
    "footer.meta": "offizielle Community-Plattform",
    "hello": "Hallo,",
    "upload.photo": "Foto hochladen"
  },

  es: {
    "nav.artistes": "Artistas",
    "nav.messages": "Mensajes",
    "nav.login": "Iniciar sesión",
    "nav.register": "Unirse",
    "nav.logout": "Cerrar sesión",
    "nav.dashboard": "Dashboard",
    "hero.eyebrow": "Plataforma oficial",
    "hero.title": "Vive el backstage, no solo el concierto.",
    "hero.subtitle": "Un espacio único donde tus opiniones realmente dan forma a las próximas canciones, videoclips y giras. Tu voz llega directamente al artista.",
    "hero.cta": "ver al artista",
    "artists.eyebrow": "Nuestros artistas",
    "artists.title": "Varios universos, una sola comunidad",
    "artists.subtitle": "Elige un artista para descubrir su universo y hablar directamente con él.",
    "artists.loading": "Cargando artistas…",
    "artists.empty": "No hay artistas publicados por el momento.",
    "artists.discover": "Descubrir →",
    "artists.conversations": "Conversaciones",
    "feat.1.title": "Un mensaje, un artista",
    "feat.1.text": "Cada conversación iniciada desde la página de un artista se le asocia automáticamente — no tienes que seleccionar nada.",
    "feat.2.title": "Leído por el artista",
    "feat.2.text": "Tus ideas de videoclips, tus canciones favoritas y tus comentarios llegan directamente al panel del artista.",
    "feat.3.title": "Decisiones, no suposiciones",
    "feat.3.text": "Las decisiones artísticas se basan en tus comentarios reales: canciones, vídeos, eventos y estrategia.",
    "cta.title": "¿Listo para hacer oír tu voz?",
    "cta.subtitle": "Crea tu cuenta en menos de un minuto y empieza la conversación.",
    "cta.button": "ver al artista",
    "messages.title": "Tus conversaciones",
    "messages.empty": "Ninguna conversación.<br>Escribe a un artista para empezar.",
    "messages.error": "No se pueden cargar los mensajes.",
    "messages.photo": "📷 Foto",
    "messages.conversation": "Conversación",
    "footer.meta": "plataforma comunitaria oficial",
    "hello": "Hola,",
    "upload.photo": "Subir una foto"
  },

  fi: {
    "nav.artistes": "Artistit",
    "nav.messages": "Viestit",
    "nav.login": "Kirjaudu sisään",
    "nav.register": "Liity",
    "nav.logout": "Kirjaudu ulos",
    "nav.dashboard": "Dashboard",
    "hero.eyebrow": "Virallinen alusta",
    "hero.title": "Koe backstage, ei vain konsertti.",
    "hero.subtitle": "Ainutlaatuinen tila, jossa palautteesi todella muokkaa seuraavia kappaleita, musiikkivideoita ja kiertueita. Äänesi menee suoraan artistille.",
    "hero.cta": "katso artisti",
    "artists.eyebrow": "Meidän artistimme",
    "artists.title": "Useita maailmoja, yksi yhteisö",
    "artists.subtitle": "Valitse artisti tutustuaksesi hänen maailmaansa ja keskustellaksesi suoraan hänen kanssaan.",
    "artists.loading": "Ladataan artisteja…",
    "artists.empty": "Ei vielä julkaistuja artisteja.",
    "artists.discover": "Tutustu →",
    "artists.conversations": "Keskustelut",
    "feat.1.title": "Yksi viesti, yksi artisti",
    "feat.1.text": "Jokainen artistin sivulta aloitettu keskustelu liitetään automaattisesti häneen — ei tarvitse valita mitään.",
    "feat.2.title": "Artisti lukee",
    "feat.2.text": "Ideasi videoista, suosikkikappaleesi ja palautteesi menevät suoraan artistin hallintapaneeliin.",
    "feat.3.title": "Päätöksiä, ei arvailuja",
    "feat.3.text": "Taiteelliset valinnat perustuvat oikeaan palautteeseesi: kappaleet, videot, tapahtumat ja strategia.",
    "cta.title": "Valmis saamaan äänesi kuuluviin?",
    "cta.subtitle": "Luo tilisi alle minuutissa ja aloita keskustelu.",
    "cta.button": "katso artisti",
    "messages.title": "Keskustelusi",
    "messages.empty": "Ei keskusteluja.<br>Kirjoita artistille aloittaaksesi.",
    "messages.error": "Viestejä ei voitu ladata.",
    "messages.photo": "📷 Kuva",
    "messages.conversation": "Keskustelu",
    "footer.meta": "virallinen yhteisöalusta",
    "hello": "Hei,",
    "upload.photo": "Lataa kuva"
  }
};

// ---------------------------------------------------------
// Détection automatique de la langue
// ---------------------------------------------------------
function detectLanguage() {
  const saved = localStorage.getItem("backstage_lang");
  if (saved && translations[saved]) return saved;

  const browserLang = (navigator.language || navigator.userLanguage || "fr").toLowerCase();

  if (browserLang.startsWith("fr")) return "fr";
  if (browserLang.startsWith("en")) return "en";
  if (browserLang.startsWith("it")) return "it";
  if (browserLang.startsWith("de")) return "de";
  if (browserLang.startsWith("es")) return "es";
  if (browserLang.startsWith("fi")) return "fi";

  // Par défaut
  return "en";
}

let currentLang = detectLanguage();

function t(key) {
  return (translations[currentLang] && translations[currentLang][key]) || 
         (translations["en"] && translations["en"][key]) || 
         key;
}

function applyTranslations() {
  document.querySelectorAll("[data-i18n]").forEach(function (el) {
    const key = el.getAttribute("data-i18n");
    const translation = t(key);

    if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
      el.placeholder = translation;
    } else {
      el.innerHTML = translation;
    }
  });

  document.documentElement.lang = currentLang;
}

function setLanguage(lang) {
  if (!translations[lang]) return;
  currentLang = lang;
  localStorage.setItem("backstage_lang", lang);
  applyTranslations();
}

document.addEventListener("DOMContentLoaded", function () {
  applyTranslations();
});