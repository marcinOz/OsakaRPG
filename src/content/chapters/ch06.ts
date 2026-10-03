import type { DialogueLine } from '@/types';

/** Chapter 6 – Leśne Obozowisko Oziema. Deep Wildwood Forest. */
export const CH06 = {
  id: 6,
  title: 'Rozdział 6',
  subtitle: 'Leśne Obozowisko Oziema',
  location: 'Głęboki Las – Polana Biwakowa',
  music: { explore: 'camp', battle: 'ch01_battle' },

  enter: [
    { speaker: 'SYSTEM', text: 'Łódź dobija do dzikiego, leśnego brzegu. Szum drzew i zapach mchu zastępują miejski smog.' },
    { speaker: 'oziem', text: 'Wreszcie. Cywilizacja zostaje z tyłu. Żadnych powiadomień, żadnego zgiełku.' },
    { speaker: 'oziem', text: 'Rozpalam ogień, rozwijajcie hamaki na drzewach. Zaraz wjeżdża prawdziwy bushcraft.' },
    { speaker: 'barti', text: 'Oziem! Rozłożyłeś już cały obóz? Ty to jesteś wariat!' },
    { speaker: 'oziem', text: 'Krzesiwo, tinderbox i hamaki już gotowe. Nauczę was sztuki przetrwania w dziczy: WILDERNESS SURVIVAL.' },
    { speaker: 'SYSTEM', text: 'Oziem dołącza do drużyny! Kompletna ekipa (6 bohaterów) jest znowu razem!' },
    { speaker: 'SYSTEM', text: 'Odblokowano umiejętność WILDERNESS SURVIVAL (leczenie drużyny + regeneracja HP).' },
    { speaker: 'danny', text: 'Panowie... to jest ten moment. Czas odpalić ognisko i otworzyć pierwsze zimne piwo!' },
  ] as DialogueLine[],
};
