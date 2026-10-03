import type { DialogueLine } from '@/types';

/** Chapter 4 – Nocny Patrol i Zaginiony Lisu. Backalleys of Old Town Starówka. */
export const CH04 = {
  id: 4,
  title: 'Rozdział 4',
  subtitle: 'Nocny Patrol i Zaginiony Lisu',
  location: 'Zaułki Starówki',
  music: { explore: 'ch04_alley', battle: 'ch01_battle' },

  enter: [
    { speaker: 'SYSTEM', text: 'Wkraczacie w ciemne zaułki Starówki. Kocia łby lśnią od nocnej wilgoci.' },
    { speaker: 'barti', text: 'Cicho... Straż Miejska i ochroniarze z klubu czeszą ten rejon.' },
    { speaker: 'alior', text: 'Widzę ich stożki widzenia. Lisu ukrył się przy śmietniku na końcu zaułka. Musimy przemknąć niezauważeni.' },
  ] as DialogueLine[],

  stealthSpotted: [
    { speaker: 'Strażnik Miejski', text: 'Stać! Kto tam chodzi po nocy bez zezwolenia?! Kontrola dokumentów!' },
    { speaker: 'danny', text: 'Spokojnie panie władzo, tylko spacerujemy! Ale jak trzeba, wezmę to na klatę!' },
  ] as DialogueLine[],

  findLisu: [
    { speaker: 'SYSTEM', text: 'Zza wielkiego metalowego śmietnika wyłania się postać w zielonym kapturze z lornetką na szyi.' },
    { speaker: 'lisu', text: 'Kurwa, prawie mnie dorwali! Stałem w cieniu przy śmietniku ze trzy minuty.' },
    { speaker: 'lisu', text: 'Zgarnijcie kiełbasę i piwa, ja spowijam dymem cały ten zaułek!' },
    { speaker: 'danny', text: 'Lisu, bracie! Masz zapasy na ognisko?' },
    { speaker: 'lisu', text: 'Mam wszystko: swojską kiełbasę, chleb i zimne browary. Ale uważajcie...' },
  ] as DialogueLine[],

  karkAmbush: [
    { speaker: 'SYSTEM', text: 'Ciężkie kroki dudnią po bruku. Z mroku wyłania się dwumetrowy bramkarz w czarnej kurtce ochroniarza!' },
    { speaker: 'Szef Ochrony "Kark"', text: 'Gdzie z tą kiełbasą i piwem?! W moim rewirze nie ma żadnych ognisk! Zmiażdżę was jak puszki po coli!' },
    { speaker: 'alior', text: 'Uwaga! Ten koleś ma pasywną odporność na zwykłe ataki fizyczne! Muszę go najpierw zestunować Frame Trapem!' },
    { speaker: 'danny', text: 'A ja wezmę jego ciosy na Steel Wall! Lisu, rzucaj dym!' },
  ] as DialogueLine[],

  afterKark: [
    { speaker: 'Szef Ochrony "Kark"', text: 'Ugh... co to za dym... nic nie widzę... tracę balans...' },
    { speaker: 'lisu', text: 'SMOKE SCREEN! Droga wolna! Zbieramy się, zanim zbiegnie się reszta posiłków!' },
    { speaker: 'SYSTEM', text: 'Lisu dołącza do drużyny! Odblokowano umiejętność SMOKE SCREEN (+50% uników i ukrycie).' },
    { speaker: 'lisu', text: 'Teraz nad wodę! Łuki czeka z motorówką przy pomoście na Marinie!' },
  ] as DialogueLine[],
};
