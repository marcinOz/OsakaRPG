import type { DialogueLine } from '@/types';

/** Chapter 5 – Nocna Misja nad Rzeką. City Marina / Lake Pier. */
export const CH05 = {
  id: 5,
  title: 'Rozdział 5',
  subtitle: 'Nocna Misja nad Rzeką',
  location: 'Przystań Marina – Pomost',
  music: { explore: 'ch05_marina', battle: 'ch01_battle' },

  enter: [
    { speaker: 'SYSTEM', text: 'Docieracie na oświetlony żółtymi latarniami drewniany pomost mariny. Woda jeziora cicho pluszcze w ciemności.' },
    { speaker: 'barti', text: 'Gdzie jest Łuki? Miał tu cumować swoją łodzią.' },
    { speaker: 'lisu', text: 'Słyszę krzyk z końca pomostu! Ktoś wpadł do lodowatej wody!' },
  ] as DialogueLine[],

  rescuePrompt: [
    { speaker: 'luki', text: 'Trzymaj koło, mordo! Trzy głębokie wdechy! Mówiłem, żeby nie skakać po pięciu shotach!' },
    { speaker: 'SYSTEM', text: 'MINI-GRA: WODNY RATUNEK! Wciśnij [SPACJA / Z], gdy wskaźnik znajdzie się w środku strefy ratunku, aby rzucić koło ratunkowe!' },
  ] as DialogueLine[],

  rescueSuccess: [
    { speaker: 'luki', text: 'TIPSY AQUA-RESCUE! Mam cię! Masz tu suchy koc i termos z herbatą z prądem. Żyjesz, kolego!' },
    { speaker: 'SYSTEM', text: 'Utopiec bezpiecznie wyciągnięty na brzeg! Hipotermia zażegnana!' },
    { speaker: 'luki', text: 'O, ekipa! Dobra nasza! Wszyscycali i zdrowi. Odpalam silnik, płyniemy na drugi brzeg do obozu Oziema!' },
    { speaker: 'SYSTEM', text: 'Łuki dołącza do drużyny! Odblokowano umiejętność TIPSY AQUA-RESCUE (oczyszczenie negatywnych efektów i wskrzeszenie).' },
    { speaker: 'danny', text: 'Wszyscy na pokład! Następny cel: dziki las Oziema!' },
  ] as DialogueLine[],
};
