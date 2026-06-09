import { redirect } from "next/navigation";

export default function CreatePage() {
  redirect("/dashboard?new=1");
}
