# Video per Classroom

Pagine "ponte" per i video SafeShare da pubblicare su Google Classroom.

**Problema:** se in Classroom incolli un link SafeShare, la scheda mostra "Just a moment..." invece del titolo. SafeShare è protetto da Cloudflare, che blocca il programma con cui Classroom legge le anteprime.

**Soluzione:** per ogni video c'è una piccola pagina su GitHub Pages con il titolo e la miniatura del video. Classroom legge quella. Quando un alunno ci clica, la pagina lo manda subito al video su SafeShare.

## Come si usa
1. Carichi il video su SafeShare e passi il link a Claude.
2. Claude crea la pagina e la pubblica.
3. Ti restituisce un link del tipo `https://teacheratwork.github.io/video-classroom/titolo-del-video/` da incollare in Classroom.

Elenco di tutte le pagine: <https://teacheratwork.github.io/video-classroom/>
