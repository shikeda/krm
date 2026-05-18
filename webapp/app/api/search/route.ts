import { type NextRequest } from 'next/server';
import { searchEntries } from '@/lib/db';

export async function GET(req: NextRequest) {
  const q = req.nextUrl.searchParams.get('q') ?? '';
  const offset = parseInt(req.nextUrl.searchParams.get('offset') ?? '0', 10);
  if (!q.trim()) return Response.json([]);
  try {
    // Quote for FTS5 phrase search
    const ftsQuery = q.replace(/"/g, '""');
    const results = searchEntries(`"${ftsQuery}"`, 50, offset);
    return Response.json(results);
  } catch (e: unknown) {
    // Fall back to prefix search if phrase search fails
    try {
      const results = searchEntries(q + '*', 50, offset);
      return Response.json(results);
    } catch {
      return Response.json({ error: String(e) }, { status: 500 });
    }
  }
}
