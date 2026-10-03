import type { DialogueLine } from '@/types';

/** Chapter 3 – Vinyl & Stare Bity. Old Town Pub "Czarny Krążek". */
export const CH03 = {
  id: 3,
  title: 'Rozdział 3',
  subtitle: 'Vinyl & Stare Bity',
  location: 'Pub "Czarny Krążek" – Rynek',
  music: { explore: 'ch03_pub', battle: 'ch01_battle' },

  enter: [
    { speaker: 'SYSTEM', text: 'Wchodzicie do pubu "Czarny Krążek". W powietrzu unosi się zapach ciemnego piwa i starego wosku winylowego.' },
    { speaker: 'barti', text: 'Co oni mi tu puszczają?! Jakiś cyfrowy plastik?! Daj mi ten igłowy gramofon, pokażę im, jak brzmi PFK i O.S.T.R. na pełnej kurwie!' },
    { speaker: 'Auto-Tune Hipster', text: 'Ej koleś, analog to przeżytek! Mój algorytm z laptopa generuje 140 BPM ze zoptymalizowanym auto-tunem!' },
    { speaker: 'Zbyt Drogie Piwo', text: 'Spróbujcie naszej nowej IPA z nutą chmielu nowozelandzkiego za 48 zł za butelkę!' },
  ] as DialogueLine[],

  beforeFight: [
    { speaker: 'barti', text: 'Panowie, ratunku! Cyfrowy plastik atakuje analogową kulturę! Danny, przytrzymaj ich, ja ładuję Bass Blast!' },
    { speaker: 'danny', text: 'Nikt nie będzie obrażał Kalibra 44 w tym lokalu! Do boju!' },
  ] as DialogueLine[],

  afterFight: [
    { speaker: 'barti', text: 'BASS BLAST ROZWALIŁ IM GŁOŚNIKI! Prawdziwy winyl zawsze wygrywa z plastikiem!' },
    { speaker: 'SYSTEM', text: 'Barti dołącza do drużyny! Odblokowano umiejętność BASS BLAST (obrażenia obszarowe + morale).' },
    { speaker: 'barti', text: 'Pakuję płyty do torby. Następny przystanek: Starówka! Musimy wyciągnąć Lisu z tarapatów.' },
    { speaker: 'alior', text: 'Według GPS Lisu utknął w zaułku za klubem. Straż Miejska i bramkarze krążą po okolicy. Czas na cichą akcję.' },
  ] as DialogueLine[],
};
