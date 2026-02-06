export interface Chronicle {
  id: string;
  date: string;    // YYYYMMDD
  time: string;    // HH:MM
  title: string;
  path: string;
  content?: string;
}

export interface DailyIndex {
  date: string;
  count: number;
}
