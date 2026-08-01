"use client";

import { useEffect, useRef, useState } from "react";
import { API_BASE_URL, apiGet, apiPost } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { DispatchWorkerRisk } from "@/lib/types";
import StatusBadge from "@/components/StatusBadge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function DispatchWorkersPage() {
  const [workers, setWorkers] = useState<DispatchWorkerRisk[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", position: "", contract_start_date: "" });
  const [submitting, setSubmitting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const load = () => {
    setLoading(true);
    apiGet<DispatchWorkerRisk[]>("/dispatch-workers")
      .then((data) => {
        setWorkers([...data].sort((a, b) => a.d_day - b.d_day));
        setError(null);
      })
      .catch(() => setError("목록을 불러오지 못했습니다. 백엔드 서버를 확인하세요."))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.contract_start_date) return;
    setSubmitting(true);
    try {
      await apiPost("/dispatch-workers", form);
      setForm({ name: "", position: "", contract_start_date: "" });
      load();
    } catch {
      setError("등록에 실패했습니다.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleExcelUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const body = new FormData();
    body.append("file", file);
    try {
      await fetch(`${API_BASE_URL}/dispatch-workers/import-excel`, {
        method: "POST",
        body,
      });
      load();
    } catch {
      setError("엑셀 업로드에 실패했습니다.");
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">파견근로자 관리</h1>
        <div className="flex gap-2">
          <Button
            variant="outline"
            nativeButton={false}
            render={<a href={`${API_BASE_URL}/dispatch-workers/export-excel`} />}
          >
            엑셀 내보내기
          </Button>
          <label className={cn(buttonVariants({ variant: "secondary" }), "cursor-pointer")}>
            엑셀 업로드
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx"
              onChange={handleExcelUpload}
              className="hidden"
            />
          </label>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
          {error}
        </div>
      )}

      <Card>
        <CardContent>
          <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-3">
            <Field label="이름">
              <Input
                required
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </Field>
            <Field label="직종">
              <Input
                value={form.position}
                onChange={(e) => setForm({ ...form, position: e.target.value })}
              />
            </Field>
            <Field label="파견시작일">
              <Input
                required
                type="date"
                value={form.contract_start_date}
                onChange={(e) => setForm({ ...form, contract_start_date: e.target.value })}
              />
            </Field>
            <Button type="submit" disabled={submitting}>
              등록
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>이름</TableHead>
                <TableHead>직종</TableHead>
                <TableHead>파견시작일</TableHead>
                <TableHead>만료예정일</TableHead>
                <TableHead>D-Day</TableHead>
                <TableHead>상태</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} className="py-6 text-center text-muted-foreground">
                    불러오는 중...
                  </TableCell>
                </TableRow>
              ) : workers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="py-6 text-center text-muted-foreground">
                    등록된 파견근로자가 없습니다.
                  </TableCell>
                </TableRow>
              ) : (
                workers.map((w) => (
                  <TableRow key={w.id}>
                    <TableCell className="font-medium">{w.name}</TableCell>
                    <TableCell>{w.position}</TableCell>
                    <TableCell>{w.contract_start_date}</TableCell>
                    <TableCell>{w.limit_date}</TableCell>
                    <TableCell>{w.d_day >= 0 ? `D-${w.d_day}` : `D+${-w.d_day}`}</TableCell>
                    <TableCell>
                      <StatusBadge status={w.status} />
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <Label>{label}</Label>
      {children}
    </div>
  );
}
