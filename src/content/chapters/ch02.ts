import type { DialogueLine } from '@/types';

/** Chapter 2 – Garażowy Krąg Walki (UFC Night). Danny & Alior HQ. */
export const CH02 = {
  id: 2,
  title: 'Rozdział 2',
  subtitle: 'Garażowy Krąg Walki (UFC Night)',
  location: 'Podziemny Kompleks Garażowy',
  music: { explore: 'ch02_garage', battle: 'ch01_battle' },

  enter: [
    { speaker: 'SYSTEM', text: 'Wchodzisz do podziemnego garażu. Pachnie olejem silnikowym, spalinami i zimnym piwem.' },
    { speaker: 'danny', text: 'O, wreszcie jesteś! Wbijaj, kurwa, właśnie McGregor dostaje oklep! Bierz browar z lodówki!' },
    { speaker: 'alior', text: 'Czekaj, zawiesiła mi się konsola. Ramki spadają! Danny, przytrzymaj go, ja odpalę Frame Trap!' },
  ] as DialogueLine[],

  wrestlingPrompt: [
    { speaker: 'danny', text: 'Ale zanim ruszymy dalej: rytuał powitalny! Szybka walka na macie z opon. Łap za bary!' },
    { speaker: 'SYSTEM', text: 'MINI-GRA: GARAŻOWE ZAPASY! Naciśnij [SPACJA / Z] w zielonym polu paska, by powalić Danny\'ego!' },
  ] as DialogueLine[],

  wrestlingWin: [
    { speaker: 'danny', text: 'Hahaha! Dobry rzut! Czuję, że kawa już zaczęła działać. Forma na wieczór jest!' },
    { speaker: 'alior', text: 'Optymalny czas reakcji: 16 milisekund. Zero lagów. Danny, bierz szejker, ja pakuję pada i zwijamy się!' },
  ] as DialogueLine[],

  neighbourInterruption: [
    { speaker: 'SYSTEM', text: 'Nagle w metalową bramę garażu ktoś zaczyna wściekle łomotać miotłą!' },
    { speaker: 'Sąsiad Szkodnik', text: 'CO TU SIĘ WYPRAWIA?! Przez ten bas szklanki mi w kredensie dzwonią! Natychmiast to wyłączyć, bo dzwonię po administrację!' },
    { speaker: 'danny', text: 'Panie sąsiedzie, UFC leci! Raz w roku ekipa się zbiera!' },
    { speaker: 'Sąsiad Szkodnik', text: 'Żadnego UFC! Po moim trupie!' },
    { speaker: 'alior', text: 'Danny, bierz go na klatę! Odpalaj Steel Wall, a ja go zglitchuję!' },
  ] as DialogueLine[],

  afterBoss: [
    { speaker: 'Sąsiad Szkodnik', text: 'Ehh... idę pisać skargę do spółdzielni... ale ten rzut przez biodro to wam ładnie wyszedł...' },
    { speaker: 'danny', text: 'Dobra nasza! Danny i Alior dołączają do ekipy!' },
    { speaker: 'SYSTEM', text: 'Danny i Alior dołączają do drużyny! Możesz teraz przełączać ich w walce.' },
    { speaker: 'alior', text: 'Kierunek: Rynek Starego Miasta. Pub "Czarny Krążek". Barti już tam czeka przy gramofonie.' },
  ] as DialogueLine[],
};
