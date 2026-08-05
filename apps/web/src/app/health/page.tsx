"use client";

import { useEffect, useState } from "react";

type HealthResponse = {
  status: string;
  db_result: number;
};

export default function HealthPage() {
  const [data, setData] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`)
      .then((response) => {
        if (!response.ok) throw new Error(`Status: ${response.status}`);
        return response.json();
      })
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <p>Error: {error}</p>;
  if (data) return <p>Health: {data.status}</p>;

  return <p>Loading...</p>;
}
