"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function DraftCard({ title, text }: { title: string; text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>{title}</CardTitle>
        <Button variant="outline" size="sm" onClick={handleCopy}>
          {copied ? "복사됨!" : "복사"}
        </Button>
      </CardHeader>
      <CardContent>
        <p className="whitespace-pre-wrap text-sm">{text}</p>
      </CardContent>
    </Card>
  );
}
