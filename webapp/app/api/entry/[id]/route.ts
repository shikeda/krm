import { type NextRequest } from 'next/server';
import { getEntry, getTSJEntry } from '@/lib/db';

export async function GET(req: NextRequest, ctx: RouteContext<'/api/entry/[id]'>) {
  const { id } = await ctx.params;
  const source = req.nextUrl.searchParams.get('source') ?? 'KRM';

  if (source === 'TSJ') {
    const entry = getTSJEntry(id);
    if (!entry) return Response.json({ error: 'Not found' }, { status: 404 });
    return Response.json(entry);
  }

  const entry = getEntry(id);
  if (!entry) return Response.json({ error: 'Not found' }, { status: 404 });
  return Response.json(entry);
}
