import { redirect } from "next/navigation";

export default function Home() {
  // For now, redirect root to Genesis 1
  redirect("/GEN/1");
}
