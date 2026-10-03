import type { DialogueLine } from '@/types';

/** Chapter 9 – Ostateczna Batalia o Wolność. Dimensional Forest Rift. */
export const CH09 = {
  id: 9,
  title: 'Rozdział 9',
  subtitle: 'Ostateczna Batalia o Wolność (The Final Boss)',
  location: 'Szczelina Międzywymiarowa Lasu',
  music: { explore: 'ch09_finalboss', battle: 'ch09_finalboss' },

  intro: [
    { speaker: 'SYSTEM', text: 'Rzeczywistość pęka na dwoje! Las zamienia się w kosmiczną arenę walki o wolność i młodość!' },
    { speaker: 'Pan Janusz', text: 'Zniszczę wasze wspomnienia! Wbiję wam pieczątkę odmowy urlopu na całe życie!' },
    { speaker: 'danny', text: 'Bierzcie pozycje bojowe! Ja biorę na klatę jego Kredyt Hipoteczny! STEEL WALL!' },
    { speaker: 'alior', text: 'Analizuję klatki animacji Janusza... Szukam okna na FRAME TRAP!' },
    { speaker: 'lisu', text: 'SMOKE SCREEN przygotowany! Oślepię audytorów!' },
    { speaker: 'barti', text: 'Wrzucam na gramofon Paktofonikę! BASS BLAST naładowany na 9999 decybeli!' },
    { speaker: 'luki', text: 'Koła ratunkowe i zimne piwo w pogotowiu! Nikt dzisiaj nie odpadnie!' },
    { speaker: 'oziem', text: 'Ogień płonie w naszych sercach! WILDERNESS SURVIVAL! DO ATAKU!' },
  ] as DialogueLine[],

  victory: [
    { speaker: 'Pan Janusz', text: 'NIEEE! Moje mandaty! Moje arkusze w Excelu... wszystko spłonęło w ogniu z Kalibrem 44 w tle...!' },
    { speaker: 'danny', text: 'I co, Janusz?! Nie ma takich rat kredytu, których ekipa nie rozwali wspólnymi siłami!' },
    { speaker: 'barti', text: 'Analogowy bas zmiótł cyfrową korporację z powierzchni ziemi!' },
    { speaker: 'oziem', text: 'Patrzcie na horyzont... mgła opada. Przychodzi świt.' },
  ] as DialogueLine[],
};
