import type { ReviewStreamMessage } from "@/lib/review-types";

type ReviewFeedbackBodyProps = {
  message: ReviewStreamMessage;
  contentClassName?: string;
  sectionClassName?: string;
};

export default function ReviewFeedbackBody({
  message,
  contentClassName = "od-bubble-content",
  sectionClassName = "od-review-sections",
}: ReviewFeedbackBodyProps) {
  const pros = message.attachment?.pros;
  const cons = message.attachment?.cons;

  if (typeof pros === "string" && typeof cons === "string") {
    return (
      <div className={sectionClassName}>
        <div className="od-review-section od-review-pros">
          <p className="od-review-label">亮点</p>
          <p className={contentClassName}>{pros}</p>
        </div>
        <div className="od-review-section od-review-cons">
          <p className="od-review-label">待改</p>
          <p className={contentClassName}>{cons}</p>
        </div>
      </div>
    );
  }

  return <p className={contentClassName}>{message.content}</p>;
}
