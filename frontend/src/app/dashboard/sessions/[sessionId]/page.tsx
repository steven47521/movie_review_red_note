import { redirect } from "next/navigation";

type PageProps = {
  params: Promise<{ sessionId: string }>;
};

export default async function SessionTimelinePage({ params }: PageProps) {
  const { sessionId } = await params;
  redirect(`/dashboard?session=${sessionId}`);
}
