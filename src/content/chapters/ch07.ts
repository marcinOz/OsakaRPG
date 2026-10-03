import type { DialogueLine } from '@/types';

/** Chapter 7 – Ognisko, Rap i Złote Czasy. All 6 heroes assembled. */
export const CH07 = {
  id: 7,
  title: 'Rozdział 7',
  subtitle: 'Ognisko, Rap i Złote Czasy',
  location: 'Nocne Ognisko w Lesie',
  music: { explore: 'camp' },

  intro: [
    { speaker: 'oziem', text: 'Ogień pali się stabilnie. Nalewajcie do kubków, panowie!' },
    { speaker: 'danny', text: 'Kurwa... niczego więcej do szczęścia dzisiaj nie trzeba.' },
  ] as DialogueLine[],

  nostalgia: [
    { speaker: 'danny', text: 'Pamiętacie, jak 15 lat temu siedzieliśmy na ławce pod blokiem bez grosza w kieszeni?' },
    { speaker: 'alior', text: 'I grało się w Gauntlet i Tekkena do czwartej rano na kineskopowym telewizorze...' },
    { speaker: 'barti', text: 'Ale bit z taśmy magnetofonowej zawsze wszedł idealnie. Kurwa, to były czasy.' },
    { speaker: 'lisu', text: 'A pamiętacie, jak uciekaliśmy przed dozorcą przez trzy podwórka? Nikt mnie wtedy nie złapał. Do dziś.' },
    { speaker: 'luki', text: 'A ja pamiętam, jak Barti wpadł do jeziora na obozie. Pierwsza akcja ratunkowa w mojej karierze.' },
    { speaker: 'barti', text: 'Miałem walkmana w kieszeni! Ratowałem kasetę, nie siebie!' },
    { speaker: 'oziem', text: 'I wtedy pierwszy raz rozpaliłem ognisko z jednej zapałki. Od tamtej pory już nie przestałem.' },
  ] as DialogueLine[],

  addWood: [
    { speaker: 'oziem', text: 'Brzoza na rozpałkę, buk na długi żar. Patrzcie i uczcie się.' },
    { speaker: 'SYSTEM', text: 'Ogień buzuje mocniej! Iskry lecą w gwiazdy.' },
  ] as DialogueLine[],
  addWoodAgain: [{ speaker: 'oziem', text: 'Starczy, bo nam hamaki spłoną. Żar jest idealny.' }] as DialogueLine[],

  playMusic: [
    { speaker: 'barti', text: 'Dobra, cisza. Wjeżdża klasyk. Głośnik na pełną.' },
    { speaker: 'SYSTEM', text: '♪ Z głośnika płynie tłusty bit inspirowany O.S.T.R. ♪' },
    { speaker: 'alior', text: 'Ten flow... 60 klatek na sekundę, mordo.' },
  ] as DialogueLine[],

  toast: [
    { speaker: 'danny', text: 'Panowie, wstajemy. Za ekipę!' },
    { speaker: 'lisu', text: 'Za tych, co zawsze wracają.' },
    { speaker: 'luki', text: 'Za to, że nikt dziś nie wpadł do rzeki. Jeszcze.' },
    { speaker: 'barti', text: 'Za stare bity i nowe wspomnienia!' },
    { speaker: 'alior', text: 'Za brak patchy, które by to zepsuły.' },
    { speaker: 'oziem', text: 'Za ogień. I za las, który należy dziś do nas.' },
    { speaker: 'SYSTEM', text: 'Morale MAX! Drużyna otrzymuje buff: KLIMAT LAT MŁODOŚCI (+50% wszystkie statystyki).' },
  ] as DialogueLine[],

  /** Teaser of chapter 8 once the ritual completes. */
  ending: [
    { speaker: 'SYSTEM', text: 'Nagle płomienie zaczynają migotać... na niebiesko.' },
    { speaker: '???', text: 'Co tu się dzieje?! Nielegalne obozowisko! Hałas po 22:00!' },
    { speaker: 'oziem', text: 'Kurwa... tylko nie on.' },
    { speaker: 'SYSTEM', text: 'CIĄG DALSZY NASTĄPI — Rozdział 8: Strażnik Leśny i Klątwa Dorosłości' },
  ] as DialogueLine[],
};
