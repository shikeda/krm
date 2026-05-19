import { type NextRequest } from 'next/server';
import { searchEntries, countEntries, getDb } from '@/lib/db';
import { expandQueryWithItaiji } from '@/lib/itaiji';

export async function GET(req: NextRequest) {
  const q = req.nextUrl.searchParams.get('q') ?? '';
  const offset = parseInt(req.nextUrl.searchParams.get('offset') ?? '0', 10);
  const itaiji = req.nextUrl.searchParams.get('itaiji') === '1';
  if (!q.trim()) return Response.json({ results: [], total_count: 0 });

  try {
    let ftsQuery: string;
    if (itaiji) {
      const db = getDb();
      const expanded = expandQueryWithItaiji(db, q);
      // 各異体字バリアントをダブルクォートで囲んでフレーズ検索し OR で結合
      ftsQuery = expanded
        .map(c => `"${c.replace(/"/g, '""')}"`)
        .join(' OR ');
    } else {
      ftsQuery = `"${q.replace(/"/g, '""')}"`;
    }

    const results = searchEntries(ftsQuery, 50, offset);
    const total_count = countEntries(ftsQuery);
    return Response.json({ results, total_count });
  } catch (e: unknown) {
    // フレーズ検索失敗時は前方一致にフォールバック
    try {
      const ftsQuery = q + '*';
      const results = searchEntries(ftsQuery, 50, offset);
      const total_count = countEntries(ftsQuery);
      return Response.json({ results, total_count });
    } catch {
      return Response.json({ error: String(e) }, { status: 500 });
    }
  }
}
