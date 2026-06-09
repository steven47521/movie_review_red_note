import MessageAvatar from "@/components/workspace/MessageAvatar";
import MessageAttachments from "@/components/workspace/MessageAttachments";
import ReviewFeedbackBody from "@/components/review-room/ReviewFeedbackBody";
import type { ImageAsset } from "@/lib/api";
import type { ReviewStreamMessage } from "@/lib/review-types";

type ReviewerBubbleProps = {
  message: ReviewStreamMessage;
  fallbackImages?: ImageAsset[];
};

export default function ReviewerBubble({
  message,
  fallbackImages = [],
}: ReviewerBubbleProps) {
  const displayName =
    message.nickname ??
    (message.role === "user"
      ? "你"
      : message.role === "moderator"
        ? "主持人"
        : message.role === "writer"
          ? "Writer"
          : message.role === "system"
            ? "系统"
            : "审稿人");

  const rowClass =
    message.role === "user"
      ? "od-bubble-row od-bubble-row-user"
      : message.role === "moderator" || message.role === "system"
        ? "od-bubble-row od-bubble-row-moderator"
        : "od-bubble-row";

  const bubbleClass =
    message.role === "user"
      ? "od-bubble od-bubble-user"
      : message.role === "moderator" || message.role === "system"
        ? "od-bubble od-bubble-moderator"
        : message.role === "writer"
          ? "od-bubble od-bubble-writer"
          : "od-bubble";

  return (
    <div className={rowClass} data-testid={`bubble-${message.role}`}>
      <MessageAvatar message={message} className="od-avatar message-avatar" />
      <div className={bubbleClass}>
        <p className="od-bubble-name">{displayName}</p>
        <ReviewFeedbackBody message={message} />
        <MessageAttachments
          attachment={message.attachment}
          fallbackImages={fallbackImages}
        />
      </div>
    </div>
  );
}
