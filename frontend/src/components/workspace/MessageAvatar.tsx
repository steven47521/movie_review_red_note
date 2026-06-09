import {
  avatarLabel,
  avatarTone,
  isReviewerMbtiAvatar,
  resolveMbti,
} from "@/lib/chat-avatar";
import type { ReviewStreamMessage } from "@/lib/review-types";

type MessageAvatarProps = {
  message: ReviewStreamMessage;
  className?: string;
};

export default function MessageAvatar({ message, className = "message-avatar" }: MessageAvatarProps) {
  const label = avatarLabel(message);
  const tone = avatarTone(message);
  const mbti = resolveMbti(message);
  const classes = [
    className,
    isReviewerMbtiAvatar(message) ? "is-mbti" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div
      className={classes}
      data-testid="message-avatar"
      data-mbti={mbti}
      title={message.role === "reviewer" && mbti ? `${mbti} 审稿人` : undefined}
      style={{
        background: `color-mix(in oklab, ${tone}, white 18%)`,
        borderColor: `color-mix(in oklab, ${tone}, white 42%)`,
        color: `color-mix(in oklab, ${tone}, black 22%)`,
      }}
      aria-hidden="true"
    >
      {label}
    </div>
  );
}
