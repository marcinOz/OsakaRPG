import type { DialogueLine } from '@/types';

/** Chapter 8 – Strażnik Leśny i Klątwa Dorosłości. Foggy Midnight Forest. */
export const CH08 = {
  id: 8,
  title: 'Rozdział 8',
  subtitle: 'Strażnik Leśny i Klątwa Dorosłości',
  location: 'Mglisty Las o Północy',
  music: { explore: 'ch08_industrial', battle: 'ch08_industrial' },

  twist: [
    { speaker: 'SYSTEM', text: 'Nagle płomień ogniska gaśnie na ułamek sekundy, po czym wybucha upiornym, lodowato-błękitnym blaskiem!' },
    { speaker: 'danny', text: 'Co do kurwy?! Ogień stał się niebieski?!' },
    { speaker: 'alior', text: 'Temperatura spadła o 20 stopni... sensory wykrywają krytyczny spadek fps-ów rzeczywistości!' },
    { speaker: 'SYSTEM', text: 'Gęsta, lodowata mgła wlewa się między sosny. Z mgły wyłania się złowroga sylwetka z megafonem i bloczkiem mandatowym!' },
    { speaker: 'Pan Janusz', text: 'CO TU SIĘ DZIEJE?! Nielegalne obozowisko! Hałas po 22:00!' },
    { speaker: 'Pan Janusz', text: 'Myśleliście, że uciekniecie przed dorosłością?! Jutro poniedziałek 8:00 rano! Marsz do domów płacić raty kredytu!' },
    { speaker: 'oziem', text: 'Po moim trupie, Janusz. Ten las należy dzisiaj do Wolnej Ekipy!' },
    { speaker: 'Pan Janusz', text: 'Naiwniacy! Przybywają moje sługi dorosłego koszmaru: KREDYT NA 30 LAT, AUDYT KORPORACYJNY i RWA KULSZOWA!' },
    { speaker: 'barti', text: 'Chłopaki, nie dajmy się złamać! Razem przetrwaliśmy 20 lat, przetrwamy i Janusza!' },
  ] as DialogueLine[],
};
