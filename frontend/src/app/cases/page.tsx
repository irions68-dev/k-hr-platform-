"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";
import type { CaseNote } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const EMPTY_FORM = {
  question: "",
  answer: "",
  exam_part: "",
  core_keyword: "",
  importance: "Medium",
};

export default function CasesPage() {
  const [cases, setCases] = useState<CaseNote[]>([]);
  const [query, setQuery] = useState("");
  const [form, setForm] = useState(EMPTY_FORM);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const search = (q: string) => {
    apiGet<CaseNote[]>(`/cases/search?q=${encodeURIComponent(q)}`).then(setCases);
  };

  useEffect(() => search(""), []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.question || !form.answer) return;
    setSubmitting(true);
    try {
      await apiPost("/cases", { ...form, legal_references: [] });
      setForm(EMPTY_FORM);
      setShowForm(false);
      search(query);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">사례 히스토리</h1>
        <Button onClick={() => setShowForm((v) => !v)}>
          {showForm ? "닫기" : "+ 새 사례"}
        </Button>
      </div>

      <Input
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          search(e.target.value);
        }}
        placeholder="키워드로 검색 (질문/답변/핵심키워드)"
      />

      {showForm && (
        <Card>
          <CardContent>
            <form onSubmit={handleSubmit} className="flex flex-col gap-3">
              <Textarea
                required
                placeholder="질문"
                value={form.question}
                onChange={(e) => setForm({ ...form, question: e.target.value })}
                rows={2}
              />
              <Textarea
                required
                placeholder="답변"
                value={form.answer}
                onChange={(e) => setForm({ ...form, answer: e.target.value })}
                rows={3}
              />
              <div className="flex flex-wrap gap-3">
                <Input
                  placeholder="시험과목"
                  value={form.exam_part}
                  onChange={(e) => setForm({ ...form, exam_part: e.target.value })}
                  className="w-auto"
                />
                <Input
                  placeholder="핵심키워드"
                  value={form.core_keyword}
                  onChange={(e) => setForm({ ...form, core_keyword: e.target.value })}
                  className="w-auto"
                />
                <Select
                  value={form.importance}
                  onValueChange={(value) => setForm({ ...form, importance: value as string })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="High">High</SelectItem>
                    <SelectItem value="Medium">Medium</SelectItem>
                    <SelectItem value="Low">Low</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button type="submit" disabled={submitting} className="self-start">
                저장
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="flex flex-col gap-3">
        {cases.length === 0 ? (
          <p className="text-sm text-muted-foreground">저장된 사례가 없습니다.</p>
        ) : (
          cases.map((c) => (
            <Card key={c.id}>
              <CardContent>
                <p className="font-medium">{c.question}</p>
                <p className="mt-1 text-sm text-muted-foreground">{c.answer}</p>
                <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                  {c.core_keyword && <Badge variant="secondary">{c.core_keyword}</Badge>}
                  {c.exam_part && <span>{c.exam_part}</span>}
                  <span>중요도: {c.importance}</span>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
