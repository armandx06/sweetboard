import Link from "next/link";

export default function Home() {
  return (
    <main>
      <h1>Health check</h1>
      <Link href="/health">Check health</Link>
    </main>
  );
}
