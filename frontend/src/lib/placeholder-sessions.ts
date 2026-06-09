export type SessionPlaceholder = {
  id: string;
  movieTitle: string;
  status: string;
  isFavorite: boolean;
  isPublished: boolean;
  updatedAt: string;
};

export const PLACEHOLDER_SESSIONS: SessionPlaceholder[] = [
  {
    id: "demo-1",
    movieTitle: "肖申克的救赎",
    status: "completed",
    isFavorite: true,
    isPublished: false,
    updatedAt: "2026-06-10",
  },
  {
    id: "demo-2",
    movieTitle: "2001太空漫游",
    status: "text_reviewing",
    isFavorite: false,
    isPublished: false,
    updatedAt: "2026-06-11",
  },
  {
    id: "demo-3",
    movieTitle: "花样年华",
    status: "image_generating",
    isFavorite: true,
    isPublished: true,
    updatedAt: "2026-06-12",
  },
];

export const STATUS_LABELS: Record<string, string> = {
  created: "已创建",
  researching: "调研中",
  angles_ready: "待选题",
  route_ready: "待定路线",
  drafting: "成稿中",
  text_reviewing: "文案审稿",
  text_finalized: "文案已定",
  image_generating: "配图生成",
  image_reviewing: "配图审稿",
  completed: "已完成",
};
