import type { DialogueLine } from '@/types';

/** Chapter 10 – Legenda Wiecznie Żywa. Sunrise over the Forest Lake. */
export const CH10 = {
  id: 10,
  title: 'Rozdział 10',
  subtitle: 'Legenda Wiecznie Żywa (Epilog)',
  location: 'Wschód Słońca nad Jeziorem Powidzkim',
  music: { explore: 'ch10_sunrise', battle: 'ch10_sunrise' },

  outro: [
    { speaker: 'SYSTEM', text: 'Złote promienie wschodzącego słońca rozświetlają taflę jeziora. Chłodna poranna bryza pachnie sosnowym igliwiem.' },
    { speaker: 'oziem', text: 'Kawa z kawiarki na żarze smakuje najlepiej na świecie. Pijcie powoli.' },
    { speaker: 'danny', text: 'Kurwa... 20 lat minęło od czasów ławki pod blokiem, a my wciąż potrafimy zebrać skład i przetrwać każdą zawieruchę.' },
    { speaker: 'alior', text: 'Żadnych lagów, żadnych spadków klatek. Czysta, bezkompromisowa synchronizacja braterstwa.' },
    { speaker: 'barti', text: 'Nawet jeśli jutro trzeba iść do roboty... to ta noc zostaje z nami na zawsze.' },
    { speaker: 'lisu', text: 'I nikt nam tego nie zabierze. Prawdziwa ekipa jest wieczna.' },
    { speaker: 'luki', text: 'Panowie, ustawcie się do pamiątkowego zdjęcia! Wyciągam aparat!' },
    { speaker: 'SYSTEM', text: '[KLIK!] Pamiątkowa fotografia została zapisana w kronice: "FRIEND PACK ANALYZER v1.0".' },
  ] as DialogueLine[],
};
