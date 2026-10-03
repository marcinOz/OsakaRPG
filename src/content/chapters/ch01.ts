import type { DialogueLine, HeroId } from '@/types';

/** Chapter 1 – Kac Gigant i Powiadomienie z Grupy. Speaker 'player' resolves to the chosen leader. */
export const CH01 = {
  id: 1,
  title: 'Rozdział 1',
  subtitle: 'Kac Gigant i Powiadomienie z Grupy',
  location: 'Mieszkanie / Poranne Miasto',
  music: { explore: 'ch01_explore', battle: 'ch01_battle' },

  wake: [
    { speaker: 'SYSTEM', text: '...bzzzt... bzzzt...' },
    {
      speaker: 'player',
      text: 'Ja pierdolę, który to rok... 2026? Głowa mi pęka, ale chłopaki już piszą na WhatsAppie. Dzisiaj nie ma opcji, żeby odpuścić.',
    },
  ] as DialogueLine[],

  /** Group chat bubbles shown in the phone popup (leader's own line is filtered out). */
  groupChat: [
    { from: 'danny', text: 'Panowie. Dziś. Bez wymówek. 💪' },
    { from: 'alior', text: 'Trasa rozpisana. Garaż → Starówka → Marina → Las. Zero lagów.' },
    { from: 'barti', text: 'Wezmę winyle. Kaliber, PFK, O.S.T.R. Kto nie przyjdzie, ten frajer.' },
    { from: 'lisu', text: 'Zrobię zaopatrzenie. Kiełbasa i browary. Cicho sza.' },
    { from: 'luki', text: 'Łódka zatankowana. Kamizelki są. Nikt nie skacze po shotach!!' },
    { from: 'oziem', text: 'Rozbijam obóz w lesie za jeziorem. Hamaki wiszą. Czekam przy ogniu. 🔥' },
  ] as { from: HeroId; text: string }[],

  hangover: [
    { speaker: 'SYSTEM', text: 'Otrzymujesz debuff: KAC GIGANT (-20% prędkości ruchu, -20% SPD w walce).' },
    {
      speaker: 'player',
      text: 'Dobra... najpierw wstać. Potem kawa. Potem ekipa.',
      leader: {
        danny: 'Dobra... kręgosłup jak po martwym ciągu 250. Kawa, białko i ruszamy po chłopaków.',
        alior: 'Input lag na poziomie 300 ms... Muszę zbić ten kac, zanim zacznę rozpisywać trasę.',
        lisu: 'Cicho... Każdy krok jak wystrzał. Kawa, i przemykam do chłopaków.',
        barti: 'W głowie mi dudni jak subwoofer bez korektora... Kawa i zbieramy ekipę.',
        oziem: 'Za długo w bloku, za mało lasu. Kawa i wychodzę na powietrze.',
        luki: 'Trzy głębokie wdechy... Nawodnienie, kawa i idziemy po chłopaków.',
      },
    },
  ] as DialogueLine[],

  backPainAmbush: [
    { speaker: 'SYSTEM', text: 'Próbujesz wstać z łóżka... Coś potężnie strzyka w lędźwiach!' },
    { speaker: 'Ból Kręgosłupa', text: 'Trzydzieści sześć lat, kolego. Myślałeś, że wstaniesz po melanżu bez rozgrzewki?' },
  ] as DialogueLine[],

  afterSpineFight: [
    { speaker: 'player', text: 'Uff... rozruszałem stawy, ale krzyż wciąż pamięta wczorajszą noc.' },
    { speaker: 'SYSTEM', text: 'Zbadaj mieszkanie! Służbowy laptop na biurku bezczelnie domaga się uwagi. Drzwi wyjściowe pozostają zablokowane.' },
  ] as DialogueLine[],

  laptop: [
    { speaker: 'SYSTEM', text: 'Laptop: 47 nieprzeczytanych wiadomości na Slacku. Temat: "PILNE – szybki call w sobotę?"' },
    { speaker: 'player', text: 'W sobotę?! Nie ma mowy, dzisiaj jest dzień z ekipą. Zamykam ten cyrk!' },
  ] as DialogueLine[],

  slackFight: [
    { speaker: 'Nieprzeczytane Slacki', text: '@here @here @here Czy ktoś może rzucić okiem na produkcję? To tylko 5 minut!' },
  ] as DialogueLine[],

  afterSlackFight: [
    { speaker: 'player', text: 'Slack wyciszony, powiadomienia zablokowane do poniedziałku. Cudowna, błoga cisza.' },
    { speaker: 'SYSTEM', text: 'Drzwi wyjściowe zostały odblokowane! Skocz do Żabki po kawę i elektrolity, by zbić kaca.' },
  ] as DialogueLine[],

  examine: {
    fridge: [{ speaker: 'SYSTEM', text: 'Lodówka: musztarda, pół cytryny i jedno samotne piwo. Zostawiasz je na wieczór.' }],
    coffeeMachine: [{ speaker: 'SYSTEM', text: 'Ekspres do kawy mruga na czerwono: "ODKAMIENIANIE". Trzeba skoczyć po kawę do Żabki.' }],
    window: [{ speaker: 'SYSTEM', text: 'Za oknem poranne blokowisko. Gołębie już dawno wstały.' }],
    poster: [{ speaker: 'SYSTEM', text: 'Plakat: "Paktofonika – Kinematografia". Trochę wyblakły. Jak wszyscy.' }],
    tv: [{ speaker: 'SYSTEM', text: 'Stary kineskop z podpiętym Pegasusem. Kiedyś grało się do czwartej rano.' }],
    bed: [{ speaker: 'SYSTEM', text: 'Łóżko wciąż kusi, ale chłopaki już piszą na grupie. Nie ma leżenia!' }],
    desk: [{ speaker: 'SYSTEM', text: 'Biurko: Slack wyciszony do poniedziałku rano. Żadne korpo ci dzisiaj nie przeszkodzi.' }],
    doorLocked: [{ speaker: 'player', text: 'Najpierw ogarnij laptopa na biurku. Inaczej ten Slack będzie dzwonił całą noc.' }],
  } as Record<string, DialogueLine[]>,

  zabka: {
    cashierWelcome: [
      { speaker: 'Kasjer z Żabki', text: 'Dzień dobry! Z czym ten hot dog? Parówka z szynki czy kabanos? Kawa mała czy duża?' },
      { speaker: 'player', text: 'Duża czarna, elektrolity i kabanos... Ratuj pan, wczoraj był potężny melanż z ekipą.' },
      { speaker: 'Kasjer z Żabki', text: 'Rozumiem bez słów, szefie. Wjeżdża zestaw ratunkowy na koszt firmy. Trzymaj się!' },
      { speaker: 'SYSTEM', text: 'Otrzymujesz: KAWA ×2, HOT DOG MAXXX ×1, ELEKTROLITY ×1! Debuff KAC GIGANT zniknął! Zespół w pełni sił!' },
      { speaker: 'player', text: 'O kurwa, wraca czucie w rękach i nogach. Pora ruszać do garażu Danny\'ego!' },
    ],
    cashierAgain: [
      { speaker: 'Kasjer z Żabki', text: 'Trzymaj się, szefie! Droga na wschód do garaży stoi otworem!' },
    ],
    hotdogs: [
      { speaker: 'SYSTEM', text: 'Roller grill: Parówki powoli obracają się na rolkach. Zapach sosu czosnkowego i prażonej cebulki jest hipnotyzujący.' },
    ],
    fridges: [
      { speaker: 'SYSTEM', text: 'Chłodziarki z napojami: Zimne Monstry, Oshee, Tyskie i krafty czekają na wieczorne ognisko w lesie.' },
    ],
    shelves: [
      { speaker: 'SYSTEM', text: 'Regał z przekąskami: Chipsy paprykowe, orzeszki i kabanosy. Podstawa każdej męskiej wyprawy.' },
    ],
  } as Record<string, DialogueLine[]>,

  city: {
    enter: [{ speaker: 'SYSTEM', text: 'Poranne Miasto. Cel: wejdź do Żabki po kawę i ruszaj na wschód do garażu Danny\'ego.' }],
    oldLady: [{ speaker: 'Sąsiadka z Ławki', text: 'Znowu się zbieracie? Pamiętam was jeszcze, jak żeście pod tym blokiem na składakach jeździli...' }],
    pigeon: [{ speaker: 'Gołąb', text: 'Gru. Gru gru.' }, { speaker: 'player', text: 'Ty też masz ciężki poranek, co?' }],
    jogger: [{ speaker: 'Biegacz w Lycrze', text: 'Dziesięć kilometrów przed śniadaniem! Spróbuj kiedyś!' }, { speaker: 'player', text: 'Spróbuję. Kiedyś. Po czterdziestce.' }],
    lamp: [{ speaker: 'SYSTEM', text: 'Zabytkowa latarnia uliczna. Wciąż delikatnie żarzy w porannym słońcu.' }],
    blocked: [{ speaker: 'player', text: 'Bez kawy i elektrolitów z Żabki nie dojdę nawet do garażu. Najpierw Żabka!' }],
    garage: [
      { speaker: 'SYSTEM', text: 'Z podziemnego garażu dudni bas i krzyki: "DAWAJ, DAWAJ!"' },
      { speaker: 'player', text: 'To na pewno oni. Czas zebrać ekipę.' },
    ],
  } as Record<string, DialogueLine[]>,
};
