import { type NextRequest } from 'next/server';
import { searchEntries, countEntries, searchTSJ, countTSJ, getDb } from '@/lib/db';
import { expandQueryWithItaiji } from '@/lib/itaiji';

export async function GET(req: NextRequest) {
  const q      = req.nextUrl.searchParams.get('q') ?? '';
  const offset = parseInt(req.nextUrl.searchParams.get('offset') ?? '0', 10);
  const itaiji = req.nextUrl.searchParams.get('itaiji') === '1';
  const source = req.nextUrl.searchParams.get('source') ?? 'KRM';
  const isTSJ  = source === 'TSJ';

  if (!q.trim()) return Response.json({ results: [], total_count: 0 });

  try {
    // KRM・TSJ 共通で異体字展開を適用
    let expandedTerms: string[] | null = null;
    let ftsQuery: string;

    if (itaiji) {
      const db = getDb();
      expandedTerms = expandQueryWithItaiji(db, q);
      ftsQuery = expandedTerms
        .map(c => `"${c.replace(/"/g, '""')}"`)
        .join(' OR ');
    } else {
      ftsQuery = `"${q.replace(/"/g, '""')}"`;
    }

    // KRM は route で組み立てた ftsQuery をそのまま渡す
    // TSJ は expandedTerms を渡して db 側でクエリを組み立てる
    const results     = isTSJ ? searchTSJ(ftsQuery, expandedTerms, 50, offset) : searchEntries(ftsQuery, 50, offset);
    const total_count = isTSJ ? countTSJ(ftsQuery, expandedTerms)              : countEntries(ftsQuery);
    return Response.json({ results, total_count });
  } catch (e: unknown) {
    // フレーズ検索失敗時は前方一致にフォールバック（itaiji 展開なし）
    try {
      const fallback    = q + '*';
      const results     = isTSJ ? searchTSJ(fallback, null, 50, offset) : searchEntries(fallback, 50, offset);
      const total_count = isTSJ ? countTSJ(fallback, null)              : countEntries(fallback);
      return Response.json({ results, total_count });
    } catch {
      return Response.json({ error: String(e) }, { status: 500 });
    }
  }
}
